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


class Sanitary(models.Model):
    name = models.CharField(
        max_length=30,
        default='',
        blank=False,
        null=False
    )
    antiparasitic = models.BooleanField(
        blank=False,
        null=False
    )
    copper = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default='',
        null=True,
        blank=True
    )
    clostridiosis = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default='',
        null=True,
        blank=True
    )
    description = models.CharField(
        max_length=1000,
        default='',
        blank=False,
        null=False
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    created_date = models.DateTimeField(auto_now_add=True)
    animal_type = models.CharField(
        choices=AnimalType.choices(),
        default=AnimalType.TERNERO,
        max_length=100
    )
    delete_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'{self.name}'

    def add_delete_date(self):
        self.delete_date = timezone.now()
        self.save()
        return f'{self.name}'
