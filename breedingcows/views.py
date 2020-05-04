from .models import BreedingCows
from animals.models import Animals, AnimalType
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from .forms import BreedingCowForm
from django.shortcuts import redirect
from django.core.paginator import Paginator
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt



def breeding_cows_list(request):
    breeding_cows_all = BreedingCows.objects.filter(leaving_date__isnull=True).order_by('entry_date')

    breeding_cows = []
    for breeding_cow in breeding_cows_all: 
        breeding_cows.append([breeding_cow, Animals.objects.all().filter(breeding_cows=breeding_cow).count()])

    paginator = Paginator(breeding_cows, 7)
    page = request.GET.get('page')
    breeding_cows_pagenated = paginator.get_page(page)

    return render(request, 'breedingcows/breeding_cows_list.html', {'breeding_cows': breeding_cows_pagenated})


@csrf_exempt
def breeding_cow_detail(request, pk):
    breeding_cow = get_object_or_404(BreedingCows, pk=pk)
    animals = []

    total = Animals.objects.all().filter(breeding_cows=breeding_cow).filter(leaving_date__isnull=True).count()
    for animal in AnimalType:
        animalsAmount = Animals.objects.all().filter(breeding_cows=breeding_cow, animal_type= animal.value).filter(leaving_date__isnull=True).count()
        if total != 0:
            animals.append([animal.value, animalsAmount, animalsAmount/total*100])

    return render(request, 'breedingcows/breeding_cow_detail.html',
                  {'breeding_cow': breeding_cow, 'animals': animals})


def breeding_cow_new(request):
    if request.method == "POST":
        form = BreedingCowForm(request.POST)
        if form.is_valid():
            breeding_cow = form.save(commit=False)
            breeding_cow.entry_date = timezone.now()
            breeding_cow.owner = request.user
            breeding_cow.status = "ACTIVO"
            breeding_cow.save()
            return redirect('breeding_cow_detail', pk=breeding_cow.pk)
    else:
        form = BreedingCowForm()
        return render(request, 'breedingcows/breeding_cow_edit.html', {'form': form})


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

    return render(request, 'breedingcows/breeding_cow_edit.html', {'form': form})


def breeding_cow_delete(request, pk):
    breeding_cow = get_object_or_404(BreedingCows, pk=pk)
    BreedingCows.add_leaving_date(breeding_cow)

    return redirect('breeding_cows_list')

class ChartData(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        breeding_cows_location = BreedingCows.objects.filter(leaving_date__isnull=True).order_by('entry_date').values_list('location', flat=True)

        breeding_cows_all = BreedingCows.objects.filter(leaving_date__isnull=True).order_by('entry_date')
        breeding_cows_animal_count = []
        breeding_cows_vacas_count = []
        breeding_cows_ternero_count = []
        breeding_cows_vaquillonas_count = []
        breeding_cows_toros_count = []
        
        animals_types = ['Vaca', 'Ternero', 'Vaquillona', 'Toro']
        vacas_count = 0
        ternero_count = 0
        vaquillonas_count = 0
        toros_count = 0

        for breeding_cow in breeding_cows_all: 
            breeding_cows_animal_count.append(Animals.objects.all().filter(breeding_cows=breeding_cow).count())
            breeding_cows_vacas_count.append(Animals.objects.all().filter(breeding_cows=breeding_cow, animal_type="Vaca").count())
            breeding_cows_ternero_count.append(Animals.objects.all().filter(breeding_cows=breeding_cow, animal_type="Ternero").count())
            breeding_cows_vaquillonas_count.append(Animals.objects.all().filter(breeding_cows=breeding_cow, animal_type="Vaquillona").count())
            breeding_cows_toros_count.append(Animals.objects.all().filter(breeding_cows=breeding_cow, animal_type="Toro").count())

            vacas_count = vacas_count + Animals.objects.all().filter(breeding_cows=breeding_cow, animal_type="Vaca").count()
            ternero_count = ternero_count + Animals.objects.all().filter(breeding_cows=breeding_cow, animal_type="Ternero").count()
            vaquillonas_count = vaquillonas_count + Animals.objects.all().filter(breeding_cows=breeding_cow, animal_type="Vaquillona").count()
            toros_count = toros_count + Animals.objects.all().filter(breeding_cows=breeding_cow, animal_type="Toro").count()

        data = {
            "breeding_cows": breeding_cows_location,
            "breeding_cows_animal_count": breeding_cows_animal_count,
            "breeding_cows_vacas_count": breeding_cows_vacas_count,
            "breeding_cows_vaquillonas_count": breeding_cows_vaquillonas_count,
            "breeding_cows_ternero_count": breeding_cows_ternero_count,
            "breeding_cows_toros_count": breeding_cows_toros_count,
            "animals_types": animals_types,
            "vacas_count": vacas_count,
            "ternero_count": ternero_count,
            "vaquillonas_count": vaquillonas_count,
            "toros_count": toros_count,
        }
        return Response(data)
