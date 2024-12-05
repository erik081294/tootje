# Generated by Django 5.1.1 on 2024-11-09 20:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cars", "0003_alter_car_options_remove_car_image_car_created_at_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="car",
            name="depreciation_fee",
            field=models.DecimalField(
                decimal_places=2,
                default=5.0,
                help_text="Afschrijvingsbijdrage per boeking",
                max_digits=6,
            ),
        ),
        migrations.AlterField(
            model_name="car",
            name="fuel_cost_per_km",
            field=models.DecimalField(
                decimal_places=2,
                default=0.21,
                help_text="Brandstofkosten per kilometer",
                max_digits=6,
            ),
        ),
        migrations.AlterField(
            model_name="car",
            name="insurance_fee",
            field=models.DecimalField(
                decimal_places=2,
                default=2.5,
                help_text="Verzekeringsbijdrage per boeking",
                max_digits=6,
            ),
        ),
        migrations.AlterField(
            model_name="car",
            name="maintenance_fee",
            field=models.DecimalField(
                decimal_places=2,
                default=2.0,
                help_text="Onderhoudsbijdrage per boeking",
                max_digits=6,
            ),
        ),
    ]
