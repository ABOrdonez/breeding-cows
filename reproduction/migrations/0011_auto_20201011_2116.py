# Generated by Django 2.2.6 on 2020-10-12 00:16

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reproduction', '0010_auto_20200916_0053'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reproduction',
            name='preparation_date',
            field=models.DateField(blank=True, default=datetime.datetime(2020, 10, 11, 21, 16, 59, 620478), null=True),
        ),
    ]
