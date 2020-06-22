from django.db import models
from enum import Enum
from django.contrib.auth.models import User



class AnimalType(Enum):
    VACA = "Vaca"
    VAQUILLONA = "Vaquillona"
    TORO = "Toro"
    TERNERO = "Ternero"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

class Diet(models.Model):
    name = models.CharField(max_length=30, default='')
    protein = models.DecimalField(max_digits=5, decimal_places=2, default='')
    energies = models.DecimalField(max_digits=5, decimal_places=2, default='')
    description = models.CharField(max_length=100, default='')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    animal_type = models.CharField(choices=AnimalType.choices(), default=AnimalType.TERNERO, max_length=100)

    def __unicode__(self):
        return u'%s' % self.name

    def __str__(self):
        return u'%s' % (self.name)
