# Generated by Django 2.2.6 on 2020-06-22 03:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('breedingcows', '0011_auto_20200622_0013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='breedingcows',
            name='description',
            field=models.CharField(default='', max_length=1000),
        ),
    ]
