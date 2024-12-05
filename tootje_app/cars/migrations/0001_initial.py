# Generated by Django 5.1.1 on 2024-09-25 14:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Car",
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
                ("brand", models.CharField(max_length=50, verbose_name="Merk")),
                ("model", models.CharField(max_length=50, verbose_name="Model")),
                ("year", models.PositiveIntegerField(verbose_name="Bouwjaar")),
                (
                    "license_plate",
                    models.CharField(max_length=10, verbose_name="Kenteken"),
                ),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="car_images/",
                        verbose_name="Foto",
                    ),
                ),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="Beschrijving"),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cars",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]