from .models import BreedingCows
from django.utils import timezone
from django.shortcuts import render, get_object_or_404


def breeding_cows_list(request):
    breeding_cows = BreedingCows.objects.filter(entry_date__lte=timezone.now()).order_by('entry_date')
    return render(request, 'breedingcowsapp/breeding_cows_list.html', {'breeding_cows': breeding_cows})


def breeding_cow_detail(request, pk):
    breeding_cow = get_object_or_404(BreedingCows, pk=pk)
    return render(request, 'breedingcowsapp/breeding_cow_detail.html', {'breeding_cow': breeding_cow})
