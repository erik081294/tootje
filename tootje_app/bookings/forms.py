from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['start_time', 'end_time', 'expected_kilometers', 'notes']
        widgets = {
            'start_time': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control',
                    'required': True,
                    'min': datetime.now().strftime('%Y-%m-%dT%H:%M')
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'end_time': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control',
                    'required': True,
                    'min': datetime.now().strftime('%Y-%m-%dT%H:%M')
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'expected_kilometers': forms.NumberInput(
                attrs={
                    'min': '1',
                    'step': '0.1',
                    'class': 'form-control'
                }
            ),
            'notes': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3
                }
            )
        }

    def clean_start_time(self):
        start_time = self.cleaned_data.get('start_time')
        if start_time:
            now = timezone.now()
            if start_time < now:
                raise ValidationError("De starttijd moet in de toekomst liggen.")
        return start_time

    def clean_end_time(self):
        end_time = self.cleaned_data.get('end_time')
        start_time = self.cleaned_data.get('start_time')
        
        if end_time and start_time:
            if end_time <= start_time:
                raise ValidationError("De eindtijd moet na de starttijd liggen.")
        return end_time

    def __init__(self, *args, **kwargs):
        self.car = kwargs.pop('car', None)
        if not self.car:
            raise ValueError("BookingForm vereist een 'car' parameter")
        
        # Get initial dates from GET parameters if available
        initial = kwargs.get('initial', {})
        if 'start' in initial:
            try:
                initial['start_time'] = datetime.fromisoformat(initial['start'])
            except (ValueError, TypeError):
                pass
        if 'end' in initial:
            try:
                initial['end_time'] = datetime.fromisoformat(initial['end'])
            except (ValueError, TypeError):
                pass
        kwargs['initial'] = initial
        
        super().__init__(*args, **kwargs)
        
        self.fields['expected_kilometers'].label = "Verwacht aantal kilometers"
        self.fields['expected_kilometers'].help_text = (
            f"Geef aan hoeveel kilometer je verwacht te rijden. "
            f"Kosten per kilometer: €{self.car.fuel_cost_per_km}/km"
        )

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if not self.car:
            raise ValidationError("Er is geen auto geselecteerd voor deze boeking.")

        if start_time and end_time:
            # Check if the car is still available
            conflicts = Booking.objects.filter(
                car=self.car,
                status='PENDING',
                start_time__lt=end_time,
                end_time__gt=start_time
            )
            
            # Exclude current booking when editing
            if self.instance and self.instance.pk:
                conflicts = conflicts.exclude(pk=self.instance.pk)
            
            if conflicts.exists():
                raise ValidationError(
                    "Deze auto is niet beschikbaar in de gekozen periode. "
                    "Kies een andere periode of een andere auto."
                )

            # Add other validations...
            min_duration = timedelta(hours=1)
            if end_time - start_time < min_duration:
                raise ValidationError("Minimale boekingsduur is 1 uur.")

        return cleaned_data