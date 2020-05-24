from django.db import models
from django.utils import timezone
from breedingcows import models as breedingcowsmodels
from enum import Enum
from diets import models as dietsmodels
from reproduction import models as reproductionmodels


class ReproductiveStatus(Enum):
    POSITIVO = "Positivo"
    NEGATIVO = "Negativo"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class AnimalType(Enum):
    VACA = "Vaca"
    VAQUILLONA = "Vaquillona"
    TORO = "Toro"
    TERNERO = "Ternero"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class AcquisitionType(Enum):
    NATURAL = "Monta natural"
    COMPRA = "Compra"
    INSEMINACION = "Inseminacio Artificial a tiempo fijo"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class DiagnosisType(Enum):
    QUISTE = "Quiste"
    ATROFIA = "Atrofia"
    DESARROLLO = "Falta de Desarrollo"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class Animals(models.Model):
    breeding_cows = models.ForeignKey(
        breedingcowsmodels.BreedingCows,
        on_delete=models.CASCADE,
        null=True,
        blank=True)
    flock_number = models.IntegerField(null=True, blank=True)
    birthday = models.DateTimeField(blank=True, null=True)
    entry_date = models.DateTimeField(default=timezone.now)
    leaving_date = models.DateTimeField(blank=True, null=True)
    rejection_date = models.DateTimeField(blank=True, null=True)
    weight = models.DecimalField(max_digits=30, decimal_places=15, default='')
    animal_type = models.CharField(
        choices=AnimalType.choices(),
        default=AnimalType.TERNERO,
        max_length=100)
    sexual_maturity = models.BooleanField(blank=True, null=True)
    body_development = models.BooleanField(blank=True, null=True)
    acquisition = models.CharField(
        choices=AcquisitionType.choices(),
        default='',
        max_length=50)
    brood = models.ManyToManyField(
        'self',
        blank=True,
        null=True,
        symmetrical=False,
        related_name='children'
    )

    def get_animal_type_label(self):
        return AnimalType(self.type).name.title()

    def __str__(self):
        return str(self.flock_number)


class AnimalDisease(models.Model):
    animal = models.ForeignKey(Animals, on_delete=models.CASCADE)
    diagnosis = models.IntegerField(
        choices=DiagnosisType.choices(),
        blank=True,
        null=True)

    def get_diagnosis_type_label(self):
        return DiagnosisType(self.type).name.title()

    def __str__(self):
        return self.location


class AnimalDiet(models.Model):
    animal = models.ForeignKey(Animals, on_delete=models.CASCADE)
    diagnosis_date = models.DateTimeField(blank=True, null=True)
    diet = models.ForeignKey(
        dietsmodels.Diet,
        on_delete=models.CASCADE,
        null=True,
        blank=True)

    def __str__(self):
        return self.diet.name


class AnimalRepoduction(models.Model):
    breeding_cow = models.ForeignKey(
        breedingcowsmodels.BreedingCows,
        on_delete=models.CASCADE,
        null=True,
        blank=True)
    animal = models.ForeignKey(Animals, on_delete=models.CASCADE)
    started_date = models.DateTimeField(blank=True, null=True)
    finished_date = models.DateTimeField(blank=True, null=True)
    reproduction = models.ForeignKey(
        reproductionmodels.Reproduction,
        on_delete=models.CASCADE)

    def __str__(self):
        return self.reproduction.reproduction_type
