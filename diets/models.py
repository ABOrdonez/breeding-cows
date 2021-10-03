from django.db import models
from enum import Enum
from django.contrib.auth.models import User
from django.utils import timezone


class AnimalType(Enum):
    VACA = "Vaca"
    VAQUILLONA = "Vaquillona"
    TORO = "Toro"
    TERNERO = "Ternero"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class Diet(models.Model):
    name = models.CharField(
        max_length=30,
        default='',
        blank=False,
        null=False
    )
    protein = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default='',
        blank=False,
        null=False
    )
    energies = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default='',
        blank=False,
        null=False
    )
    description = models.CharField(max_length=1000, default='')
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    created_on = models.DateTimeField(
        auto_now_add=True,
        blank=False,
        null=False
    )
    animal_type = models.CharField(
        choices=AnimalType.choices(),
        default=AnimalType.TERNERO,
        max_length=100,
        blank=False,
        null=False
    )
    delete_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'{self.name}'

    def add_delete_date(self):
        self.delete_date = timezone.now()
        self.save()
        return f'{self.name}'
