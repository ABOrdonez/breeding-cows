from .models import BreedingCows
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from .forms import BreedingCowForm
from django.shortcuts import redirect


def breeding_cows_list(request):
    breeding_cows = BreedingCows.objects.filter(entry_date__lte=timezone.now()).order_by('entry_date')
    return render(request, 'breedingcowsapp/breeding_cows_list.html', {'breeding_cows': breeding_cows})


def breeding_cow_detail(request, pk):
    breeding_cow = get_object_or_404(BreedingCows, pk=pk)
    return render(request, 'breedingcowsapp/breeding_cow_detail.html', {'breeding_cow': breeding_cow})

def breeding_cow_new(request):
    if request.method == "POST":
        form = BreedingCowForm(request.POST)
        if form.is_valid():
            breeding_cow = form.save(commit=False)
            breeding_cow.entry_date = timezone.now()
            breeding_cow.save()
            return redirect('breeding_cow_detail', pk=breeding_cow.pk)

    else:
        form = BreedingCowForm()
        return render(request, 'breedingcowsapp/breeding_cow_edit.html', {'form': form})


def breeding_cow_edit(request, pk):
    breeding_cow = get_object_or_404(BreedingCows, pk=pk)
    if request.method == "POST":
        form = BreedingCowForm(request.POST, instance=breeding_cow)
        if form.is_valid():
            breeding_cow = form.save(commit=False)
            breeding_cow.save()
            return redirect('breeding_cow_detail', pk=breeding_cow.pk)
    else:
        form = BreedingCowForm(instance=breeding_cow)
    return render(request, 'breedingcowsapp/breeding_cow_edit.html', {'form': form})
