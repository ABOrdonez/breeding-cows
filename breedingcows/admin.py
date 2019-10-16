from django.contrib import admin
from .models import Animal
from .models import BreedingCows

admin.site.register(BreedingCows)
admin.site.register(Animal)
