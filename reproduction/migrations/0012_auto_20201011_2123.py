# Generated by Django 2.2.6 on 2020-10-12 00:23

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reproduction', '0011_auto_20201011_2116'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reproduction',
            name='preparation_date',
            field=models.DateField(blank=True, default=datetime.datetime(2020, 10, 11, 21, 23, 19, 48371), null=True),
        ),
    ]