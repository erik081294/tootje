# Generated by Django 5.1.1 on 2024-11-07 20:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("cars", "0003_alter_car_options_remove_car_image_car_created_at_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Booking",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("start_time", models.DateTimeField()),
                ("end_time", models.DateTimeField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "In afwachting"),
                            ("APPROVED", "Goedgekeurd"),
                            ("REJECTED", "Afgewezen"),
                            ("COMPLETED", "Voltooid"),
                            ("CANCELLED", "Geannuleerd"),
                        ],
                        default="PENDING",
                        max_length=20,
                    ),
                ),
                (
                    "total_cost",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("notes", models.TextField(blank=True)),
                (
                    "fuel_cost",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
                ),
                (
                    "insurance_cost",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
                ),
                (
                    "maintenance_cost",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
                ),
                (
                    "depreciation_cost",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
                ),
                (
                    "car",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bookings",
                        to="cars.car",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bookings",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-start_time"],
            },
        ),
    ]
