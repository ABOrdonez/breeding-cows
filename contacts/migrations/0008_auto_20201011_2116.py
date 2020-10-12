# Generated by Django 2.2.6 on 2020-10-12 00:16

import contacts.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0007_auto_20200916_0053'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='civil_status',
            field=models.CharField(choices=[('Soltero', 'SOLTERO'), ('Casado', 'CASADO'), ('Divorciado', 'DIVORCIADO')], default=contacts.models.CivilStatus('Soltero'), max_length=50),
        ),
        migrations.AlterField(
            model_name='contact',
            name='direction',
            field=models.CharField(default='', max_length=300),
        ),
        migrations.AlterField(
            model_name='contact',
            name='first_name',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='contact',
            name='last_name',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='contact',
            name='phone',
            field=models.IntegerField(default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='contact',
            name='province',
            field=models.CharField(default='', max_length=100),
        ),
    ]