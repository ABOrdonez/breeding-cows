from django.db import models
from enum import Enum
from datetime import datetime


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
    # TODO VALIDAR SI PASAN 120 DIAS
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

    def has_execution_type_before_next_date(self):
        if self.preparation_date and not self.execution_date:
            return datetime.now().date() < self.next_date
        return False

    def has_execution_type_in_same_specified_days(self):
        if self.preparation_date and not self.execution_date:
            return datetime.now().date() == self.next_date
        return False

    def has_execution_type_after_specified_days(self):
        if self.preparation_date and not self.execution_date:
            return datetime.now().date() > self.next_date
        return False

    def has_execution_before_next_date(self):
        if self.execution_date and not self.revision_date:
            return datetime.now().date() < self.next_date
        return False

    def has_execution_in_same_specified_days(self):
        if self.execution_date and not self.revision_date:
            return datetime.now().date() == self.next_date
        return False

    def has_execution_after_specified_days(self):
        if self.execution_date and not self.revision_date:
            return datetime.now().date() > self.next_date
        return False

    def has_revision_before_next_date(self):
        if self.revision_date and not self.separation_date:
            return datetime.now().date() < self.next_date
        return False

    def has_revision_in_same_specified_days(self):
        if self.revision_date and not self.separation_date:
            return datetime.now().date() == self.next_date
        return False

    def has_revision_after_specified_days(self):
        if self.revision_date and not self.separation_date:
            return datetime.now().date() > self.next_date
        return False

    def has_separation_before_next_date(self):
        if self.separation_date and not self.give_birth_date:
            return datetime.now().date() < self.next_date
        return False

    def has_separation_in_same_specified_days(self):
        if self.separation_date and not self.give_birth_date:
            return datetime.now().date() == self.next_date
        return False

    def has_separation_after_specified_days(self):
        if self.separation_date and not self.give_birth_date:
            return datetime.now().date() > self.next_date
        return False

    def __str__(self):
        return f'{self.reproduction_type}'
