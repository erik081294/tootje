from django.db import models
from django.contrib.auth.models import User

class Car(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cars')
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    license_plate = models.CharField(max_length=10)
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    fuel_cost_per_km = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        default=0.21,
        help_text="Brandstofkosten per kilometer"
    )
    insurance_fee = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        default=2.50,
        help_text="Verzekeringsbijdrage per boeking"
    )
    maintenance_fee = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        default=2.00,
        help_text="Onderhoudsbijdrage per boeking"
    )
    depreciation_fee = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        default=5.00,
        help_text="Afschrijvingsbijdrage per boeking"
    )

    def __str__(self):
        return f"{self.brand} {self.model} ({self.license_plate})"

    class Meta:
        ordering = ['-created_at']