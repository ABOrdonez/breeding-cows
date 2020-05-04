from django.shortcuts import render, get_object_or_404
from .models import Diet
from .forms import DietForm
from animals.models import AnimalDiet
from django.utils import timezone
from django.shortcuts import redirect



def diets_list(request):
    diets_list = Diet.objects.order_by('name')

    diets =[]
    for diet in diets_list: 
        diets.append([diet, AnimalDiet.objects.all().filter(diet=diet).count()])

    return render(request, 'diets/diets_list.html', {'diets': diets})


def diet_detail(request, pk):
    diet = get_object_or_404(Diet, pk=pk)

    return render(request, 'diets/diet_detail.html', {'diet': diet})


def diet_edit(request, pk):
    diet = get_object_or_404(Diet, pk=pk)
    if request.method == "POST":
        form = DietForm(request.POST, instance=diet)
        if form.is_valid():
            diet = form.save(commit=False)
            diet.save()
            return redirect('diet_detail', pk=diet.pk)
            
    else:
        form = DietForm(instance=diet)
    return render(request, 'diets/diet_edit.html', {'form': form})


def diet_new(request):
    if request.method == "POST":
        form = DietForm(request.POST)
        if form.is_valid():
            diet = form.save(commit=False)
            diet.created_on = timezone.now()
            diet.owner = request.user
            diet.save()
            return redirect('diet_detail', pk=diet.pk)

    else:
        form = DietForm()
        return render(request, 'diets/diet_edit.html', {'form': form})