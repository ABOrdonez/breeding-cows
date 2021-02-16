from django.contrib import admin
from .models import (Animals, AnimalDisease, AnimalDiet, AnimalRepoduction, AnimalSanitary)


admin.site.register(Animals)
admin.site.register(AnimalDisease)
admin.site.register(AnimalDiet)
admin.site.register(AnimalRepoduction)
admin.site.register(AnimalSanitary)
