from django import forms
from .models import Car

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = [
            'brand', 'model', 'year', 'license_plate', 'hourly_rate',
            'fuel_cost_per_km', 'insurance_fee', 'maintenance_fee',
            'depreciation_fee', 'description'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['brand'].help_text = "Bijvoorbeeld: Toyota, Volkswagen, etc."
        self.fields['model'].help_text = "Bijvoorbeeld: Corolla, Golf, etc."
        self.fields['year'].help_text = "Bouwjaar van de auto"
        self.fields['hourly_rate'].help_text = "Basis uurtarief voor het gebruik van de auto"