# Generated by Django 2.2.6 on 2020-07-19 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diets', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='diet',
            name='description',
            field=models.CharField(default='', max_length=1000),
        ),
    ]