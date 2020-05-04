# Generated by Django 2.2.6 on 2019-11-11 20:23

import animals.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('action', '0002_actiondetail'),
    ]

    operations = [
        migrations.RenameField(
            model_name='actiondetail',
            old_name='next_date',
            new_name='birth_date',
        ),
        migrations.RemoveField(
            model_name='actiondetail',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='actiondetail',
            name='realization_date',
        ),
        migrations.AddField(
            model_name='actiondetail',
            name='reproductive_status',
            field=models.CharField(choices=[('Positivo', 'POSITIVO'), ('Negativo', 'NEGATIVO')], default=animals.models.ReproductiveStatus('Positivo'), max_length=100),
        ),
    ]
