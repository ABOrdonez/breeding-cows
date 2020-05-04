from django.db import models
from django.contrib.auth.models import User
from enum import Enum
from django.utils import timezone
from contacts import models as contactsmodels
from contacts.models import Contact


class PositionType(Enum):
    DUEÑO = "Dueño"
    PEON = "Peón"
    VETERINARIO = "Veterinario"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class StatusType(Enum):
    ACTIVO = "Activo"
    ELIMINADO = "Eliminado"
    SUSPENDIDIO = "Suspendido"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class BreedingCows(models.Model):
    location = models.CharField(max_length=50, null=False, blank=False, default='')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, null=True, blank=True)
    entry_date = models.DateTimeField(blank=True, null=True)
    leaving_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=StatusType.choices(), default=StatusType.ACTIVO)

    def get_status_type_label(self):
        return StatusType(self.type).name.title()

    def add_leaving_date(self):
        self.leaving_date = timezone.now()
        self.save()
        return self.location

    def __str__(self):
        return self.location


class WorkPosition(models.Model):
    breeding_cows = models.ForeignKey(BreedingCows, on_delete=models.CASCADE)
    person = models.ForeignKey(contactsmodels.Contact, on_delete=models.CASCADE, null=True, blank=True)
    entry_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(choices=StatusType.choices(), default=StatusType.ACTIVO, max_length=50)
    position = models.CharField(choices=PositionType.choices(), default=PositionType.DUEÑO, max_length=50)

    def get_position_type_label(self):
        return PositionType(self.type).name.title()

    def get_status_type_label(self):
        return StatusType(self.type).name.title()

    def __str__(self):
        return self.person.username
