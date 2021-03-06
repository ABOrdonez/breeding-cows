# Generated by Django 2.2.6 on 2019-11-11 18:49

import animals.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('animals', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='animals',
            name='animal_type',
            field=models.CharField(choices=[('Vaca', 'VACA'), ('Vaquillona', 'VAQUILLONA'), ('Toro', 'TORO'), ('Ternero', 'TERNERO')], default=animals.models.AnimalType('Ternero'), max_length=100),
        ),
        migrations.AlterField(
            model_name='animals',
            name='reproductive_status',
            field=models.CharField(choices=[('Positivo', 'POSITIVO'), ('Negativo', 'NEGATIVO')], default=animals.models.ReproductiveStatus('Positivo'), max_length=100),
        ),
    ]
