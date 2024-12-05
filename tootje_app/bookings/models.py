from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
import pytz
from cars.models import Car
from decimal import Decimal
from datetime import datetime

class Booking(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'In afwachting'),
        ('APPROVED', 'Goedgekeurd'),
        ('REJECTED', 'Afgewezen'),
        ('COMPLETED', 'Voltooid'),
        ('CANCELLED', 'Geannuleerd'),
    ]

    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    fuel_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    insurance_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    maintenance_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    depreciation_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    expected_kilometers = models.DecimalField(
        max_digits=6, 
        decimal_places=1, 
        default=50.0,
        help_text="Verwacht aantal kilometers"
    )

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.car} - {self.user} - {self.start_time.date()}"

    def calculate_total_cost(self):
        """Verbeterde kostencalculatie met alle componenten"""
        if not self.start_time or not self.end_time:
            return Decimal('0.00')
        
        duration = self.end_time - self.start_time
        hours = duration.total_seconds() / 3600
        
        # Basis uurtarief
        base_cost = Decimal(str(hours)) * self.car.hourly_rate
        
        # Extra kosten nu met verwachte kilometers
        self.fuel_cost = self.car.fuel_cost_per_km * self.expected_kilometers
        self.insurance_cost = self.car.insurance_fee
        self.maintenance_cost = self.car.maintenance_fee
        self.depreciation_cost = self.car.depreciation_fee
        
        return (base_cost + self.fuel_cost + self.insurance_cost + 
                self.maintenance_cost + self.depreciation_cost)

    def clean(self):
        """Validate the booking"""
        super().clean()
        
        if not self.car:
            raise ValidationError({
                'car': "Een auto moet geselecteerd zijn voor deze boeking."
            })

        if not self.start_time or not self.end_time:
            raise ValidationError({
                'start_time': "Start- en eindtijd zijn verplicht." if not self.start_time else None,
                'end_time': "Start- en eindtijd zijn verplicht." if not self.end_time else None
            })

        # Skip future start time validation if booking is being cancelled
        if self.status != 'CANCELLED':
            # Check if start time is in the future
            now = timezone.now()
            if self.start_time < now:
                raise ValidationError({
                    'start_time': "Starttijd moet in de toekomst liggen."
                })

        # Check if end time is after start time
        if self.end_time <= self.start_time:
            raise ValidationError({
                'end_time': "Eindtijd moet na starttijd liggen."
            })

        # Check for overlapping bookings
        overlapping_bookings = Booking.objects.filter(
            car=self.car,
            status__in=['PENDING', 'APPROVED'],
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        )

        # Exclude current booking when updating
        if self.pk:
            overlapping_bookings = overlapping_bookings.exclude(pk=self.pk)

        if overlapping_bookings.exists():
            raise ValidationError({
                '__all__': "Deze auto is al geboekt voor (een deel van) deze periode."
            })

    def save(self, *args, **kwargs):
        # Zorg ervoor dat de tijden in UTC worden opgeslagen
        if self.start_time and not timezone.is_aware(self.start_time):
            self.start_time = timezone.make_aware(self.start_time, pytz.UTC)
        if self.end_time and not timezone.is_aware(self.end_time):
            self.end_time = timezone.make_aware(self.end_time, pytz.UTC)
            
        self.clean()
        if not self.total_cost:
            self.total_cost = self.calculate_total_cost()
        super().save(*args, **kwargs)

    @classmethod
    def get_available_times(cls, car, date):
        """Get available time slots for a specific car and date"""
        bookings = cls.objects.filter(
            car=car,
            status__in=['PENDING', 'APPROVED'],
            start_time__date=date
        ).order_by('start_time')
        
        return bookings