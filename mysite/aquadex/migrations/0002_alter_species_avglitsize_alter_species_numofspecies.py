# Generated by Django 5.0.4 on 2024-05-07 08:56

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("aquadex", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="species",
            name="avgLitSize",
            field=models.SmallIntegerField(
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(50),
                ],
                verbose_name="Average Litter Size",
            ),
        ),
        migrations.AlterField(
            model_name="species",
            name="numOfSpecies",
            field=models.SmallIntegerField(
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(50),
                ],
                verbose_name="Number of Species",
            ),
        ),
    ]
