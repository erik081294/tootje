from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Add additional fields
    # ...

    def __str__(self):
        return f'{self.user.username} Profile'

class PaymentHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.user.username} - {self.amount} - {self.date}'
