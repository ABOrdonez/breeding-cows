# Generated by Django 3.1.4 on 2021-01-25 00:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('breedingcows', '0013_auto_20200622_0055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='breedingcows',
            name='entry_date',
            field=models.DateTimeField(default=datetime.datetime(1900, 1, 1, 0, 0)),
            preserve_default=False,
        ),
    ]
