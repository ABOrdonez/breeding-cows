# Generated by Django 2.2.6 on 2020-09-16 03:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reproduction', '0009_reproduction_next_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reproduction',
            name='preparation_date',
            field=models.DateField(blank=True, default=datetime.datetime(2020, 9, 16, 0, 53, 31, 670828), null=True),
        ),
    ]
