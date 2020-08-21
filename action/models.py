from django.db import models
from animals import models as animalsmodels
from breedingcows import models as breedingcowsmodels
from django.utils import timezone
from django.contrib.auth.models import User


class ActionDefinition(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False, default='')
    description = models.CharField(max_length=200, null=False, blank=False, default='')
    animal_type = models.CharField(choices=animalsmodels.AnimalType.choices(), default=animalsmodels.AnimalType.TERNERO,
                                   max_length=100)

    def __str__(self):
        return self.name


class Action(models.Model):
    action = models.ForeignKey(ActionDefinition, on_delete=models.CASCADE, null=True, blank=True)
    breeding_cows = models.ForeignKey(breedingcowsmodels.BreedingCows, on_delete=models.CASCADE, null=True, blank=True)
    realization_date = models.DateTimeField(default=timezone.now)
    next_date = models.DateTimeField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.action.name


class ActionDetail(models.Model):
    action = models.ForeignKey(Action, on_delete=models.CASCADE, null=True, blank=True)
    animal = models.ForeignKey(animalsmodels.Animals, on_delete=models.CASCADE, null=True, blank=True)
    birth_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.action.action.name
