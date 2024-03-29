from django.db import models
from django.contrib.auth.models import User
from enum import Enum
from django.utils import timezone


class CivilStatus(Enum):
    SOLTERO = "Soltero"
    CASADO = "Casado"
    DIVORCIADO = "Divorciado"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class Contact(models.Model):
    first_name = models.CharField(
        max_length=50,
        default='',
        blank=False,
        null=False
    )
    last_name = models.CharField(
        max_length=50,
        default='',
        blank=False,
        null=False
    )
    phone = models.IntegerField(
        default='',
        blank=False,
        null=False
    )
    email = models.EmailField(default='')
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    entry_date = models.DateTimeField(blank=True, null=True)
    birthday = models.DateTimeField(blank=True, null=True, default='')
    direction = models.CharField(
        max_length=300,
        default='',
        blank=False,
        null=False
    )
    province = models.CharField(
        max_length=100,
        default='',
        blank=False,
        null=False
    )
    civil_status = models.CharField(
        choices=CivilStatus.choices(),
        default=CivilStatus.SOLTERO,
        max_length=50)
    delete_date = models.DateTimeField(blank=True, null=True)

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def add_delete_date(self):
        self.delete_date = timezone.now()
        self.save()
        return f'{self.first_name}'
