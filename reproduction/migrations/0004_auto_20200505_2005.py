# Generated by Django 2.2.6 on 2020-05-05 23:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reproduction', '0003_auto_20200503_1808'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reproduction',
            old_name='separation',
            new_name='separation_date',
        ),
    ]
