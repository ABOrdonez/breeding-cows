from django.shortcuts import render
from django.shortcuts import render
from .models import BreedingCows
from django.utils import timezone


def breeding_cows_list(request):
    breeding_cows = BreedingCows.objects.filter(entry_date__lte=timezone.now()).order_by('entry_date')
    return render(request, 'breedingcowsapp/breeding_cows_list.html', {'breeding_cows':breeding_cows})
