# Generated by Django 2.2.6 on 2020-05-24 21:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('animals', '0012_auto_20200523_1305'),
    ]

    operations = [
        migrations.AlterField(
            model_name='animals',
            name='brood',
            field=models.ManyToManyField(blank=True, null=True, related_name='children', to='animals.Animals'),
        ),
    ]
