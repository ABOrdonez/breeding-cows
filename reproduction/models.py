from django.db import models
from enum import Enum


class ReproductionType(Enum):
    INSEMINACION = "Inseminacion Artificial"
    NATURAL = "Natural"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class ReproductionProcessDays(Enum):
    EXECUTION = 7
    REVISION = 30
    SEPARATION = 90
	#TODO VALIDAR SI PASAN 120 DIAS
    GIVE_BIRTH = 120
    REPEAT_PROCESS = 60

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class Reproduction(models.Model):
    has_prostaglandin_vaccine = models.BooleanField(blank=True, null=True)
    has_vaginal_device = models.BooleanField(blank=True, null=True)
    reproduction_type = models.CharField(
        choices=ReproductionType.choices(),
        default='',
        max_length=100
    )
    potential_give_birth_date = models.DateField(blank=True, null=True)
    preparation_date = models.DateField(blank=True, null=True)
    execution_date = models.DateField(blank=True, null=True)
    revision_date = models.DateField(blank=True, null=True)
    success_revision = models.BooleanField(blank=True, null=True)
    separation_date = models.DateField(blank=True, null=True)
    give_birth_date = models.DateField(blank=True, null=True)
    next_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.reproduction_type
