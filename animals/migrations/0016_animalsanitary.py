# Generated by Django 2.2.6 on 2020-05-26 00:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sanitarybook', '0002_auto_20200525_1650'),
        ('animals', '0015_auto_20200525_1652'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnimalSanitary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('done_date', models.DateField(blank=True, null=True)),
                ('animal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='animals.Animals')),
                ('sanitary', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sanitarybook.Sanitary')),
            ],
        ),
    ]
