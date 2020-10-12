# Generated by Django 2.2.6 on 2020-09-16 03:53

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('animals', '0017_auto_20200526_0043'),
    ]

    operations = [
        migrations.AlterField(
            model_name='animals',
            name='birthday',
            field=models.DateField(default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='animals',
            name='entry_date',
            field=models.DateField(default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='animals',
            name='weight',
            field=models.DecimalField(decimal_places=2, default='', max_digits=30),
        ),
        migrations.AlterField(
            model_name='animalsanitary',
            name='sanitary',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='sanitarybook.Sanitary'),
        ),
    ]