from django.db import models
from django.utils import timezone

status = (
    ('a', 'Activo'),
    ('e', 'Eliminado'),
)

reproductive_status = (
    ('p', 'Positivo'),
    ('n', 'Negativo'),
)

animal_type = (
    ('v', 'Vaca'),
    ('va', 'Vaquillona'),
    ('t', 'Toro'),
    ('te', 'ternero')
)


class BreedingCows(models.Model):
    location = models.CharField(max_length=50, null=False, blank=False, default='')
    entry_date = models.DateTimeField(blank=True, null=True)
    leaving_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=1, choices=status, blank=True, default='a',
                              help_text='Estado del Rodeo de Cría')

    def __str__(self):
        return self.location


class Animal(models.Model):
    breeding_cows = models.ForeignKey(BreedingCows, on_delete=models.CASCADE)
    flock_number = models.IntegerField(null=True, blank=True, default=0)
    birthday = models.DateTimeField(blank=True, null=True)
    entry_date = models.DateTimeField(default=timezone.now)
    leaving_date = models.DateTimeField(blank=True, null=True)
    rejection_date = models.DateTimeField(blank=True, null=True)
    weight = models.DecimalField(max_digits=30, decimal_places=15)
    reproductive_status = models.CharField(max_length=1, choices=reproductive_status, blank=True, default='p',
                                           help_text='Estado reproductorio del animal')
    animal_type = models.CharField(max_length=1, choices=animal_type, blank=True, default='t',
                                   help_text='Estado reproductorio del animal')

    def rejection(self):
        self.rejection_date = timezone.now()
        self.animal_type = "n"
        self.save()

    def __str__(self):
        return self.flock_number
