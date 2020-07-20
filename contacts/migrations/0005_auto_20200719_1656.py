# Generated by Django 2.2.6 on 2020-07-19 19:56

import contacts.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0004_auto_20200222_1558'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contact',
            options={},
        ),
        migrations.AddField(
            model_name='contact',
            name='civil_status',
            field=models.CharField(choices=[('Soltero', 'SOLTERO'), ('Casado', 'CASADO'), ('Divorciado', 'DIVORCIADO')], default=contacts.models.CivilStatus('Soltero'), max_length=100),
        ),
        migrations.AddField(
            model_name='contact',
            name='direction',
            field=models.CharField(default='', max_length=30),
        ),
        migrations.AddField(
            model_name='contact',
            name='province',
            field=models.CharField(default='', max_length=30),
        ),
    ]
