from django.shortcuts import render, get_object_or_404
from .models import Diet
from .forms import DietForm
from animals.models import AnimalDiet, Animals
from django.utils import timezone
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.paginator import Paginator


def diets_list(request):
    diets_list = Diet.objects.order_by('name')
    diets = []

    for diet in diets_list:
        diets.append([
            diet,
            AnimalDiet.objects.all().filter(diet=diet).count()
        ])

    paginator = Paginator(diets, 4)
    page = request.GET.get('page')
    diets_pagenated = paginator.get_page(page)

    return render(request, 'diets/diets_list.html', {'diets': diets_pagenated})


def diet_detail(request, pk):
    diet = get_object_or_404(Diet, pk=pk)
    animals = AnimalDiet.objects.values_list(
        'animal',
        flat=True
    ).filter(
        diet=diet
    )
    breeding_cows_list = []

    for animal in animals:
        animalposta = get_object_or_404(Animals, pk=animal)
        breeding_cows_list.append(animalposta.breeding_cows)

    return render(
        request,
        'diets/diet_detail.html',
        {
            'diet': diet,
            'animal_count': len(animals),
            'breeding_cows_count': len(set(breeding_cows_list))
        }
    )


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
    return render(
        request,
        'diets/diet_edit.html',
        {
            'form': form,
            'message': True
        }
    )


def diet_new(request):
    success = True
    if request.method == "POST":
        form = DietForm(request.POST)
        if form.is_valid():
            print("valido")
            diet = form.save(commit=False)
            diet.created_on = timezone.now()
            diet.owner = request.user
            diet.save()
            return redirect('diet_detail', pk=diet.pk)
        else:
            success = False

    else:
        form = DietForm()
    return render(
        request,
        'diets/diet_edit.html',
        {
            'form': form,
            'message': success
        }
    )


class ChartData(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        diets_name = Diet.objects.order_by(
            'name'
        ).values_list(
            'name',
            flat=True
        )
        diet_animal_types = Diet.objects.order_by(
            'name'
        ).values_list(
            'animal_type',
            flat=True
        )
        diet_proteins = Diet.objects.order_by(
            'name'
        ).values_list(
            'protein',
            flat=True
        )
        diet_energies = Diet.objects.order_by(
            'name'
        ).values_list(
            'energies',
            flat=True
        )
        diets_all = Diet.objects.order_by('name')

        diets_animal_count = []

        for diet in diets_all:
            diets_animal_count.append(
                AnimalDiet.objects.all().filter(diet=diet).count()
            )

        data = {
            "diets": diets_name,
            "diet_animal_types": diet_animal_types,
            "diet_proteins": diet_proteins,
            "diet_energies": diet_energies,
            "diets_animal_count": diets_animal_count,
        }
        return Response(data)
