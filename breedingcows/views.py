from .models import BreedingCows
from animals.models import Animals, AnimalType, AnimalRepoduction
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from .forms import BreedingCowForm
from django.shortcuts import redirect
from django.core.paginator import Paginator
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from reproduction.models import ReproductionProcessDays


def breeding_cows_list(request):
    breeding_cows_all = BreedingCows.objects.filter(
        leaving_date__isnull=True).order_by(
        'entry_date')
    breeding_cows = []

    for breeding_cow in breeding_cows_all:
        breeding_cows.append([breeding_cow, Animals.objects.filter(
            breeding_cows=breeding_cow).count()])

    paginator = Paginator(breeding_cows, 7)
    page = request.GET.get('page')
    breeding_cows_pagenated = paginator.get_page(page)

    return render(
        request,
        'breedingcows/breeding_cows_list.html',
        {'breeding_cows': breeding_cows_pagenated})


@csrf_exempt
def breeding_cow_detail(request, pk):
    breeding_cow = get_object_or_404(BreedingCows, pk=pk)
    animals_info = []
    total = Animals.objects.filter(
        breeding_cows=breeding_cow,
        leaving_date__isnull=True).count()
    animals = Animals.objects.filter(
        breeding_cows=breeding_cow,
        leaving_date__isnull=True)

    for animal in AnimalType:
        animalsAmount = Animals.objects.filter(
            breeding_cows=breeding_cow,
            animal_type=animal.value,
            leaving_date__isnull=True).count()
        if total != 0:
            percentage = animalsAmount / total * 100
            animals_info.append([animal.value, animalsAmount, percentage])

    on_time_amount = count_reproduction_process_before(animals, 30)
    warning_amount = count_reproduction_process_before(animals, 0)
    danger_amount = count_reproduction_process_on_danger(animals)

    return render(request, 'breedingcows/breeding_cow_detail.html', {
        'breeding_cow': breeding_cow,
        'animals': animals_info,
        'on_time_amount': on_time_amount,
        'warning_amount': warning_amount,
        'danger_amount': danger_amount
    })


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


def count_reproduction_process_before(animals, days):
    reproduction_count = 0
    execution_days = ReproductionProcessDays.EXECUTION.value + days
    revision_days = ReproductionProcessDays.REVISION.value + days
    separation_days = ReproductionProcessDays.SEPARATION.value + days
    give_birth_days = ReproductionProcessDays.GIVE_BIRTH.value + days

    for animal in animals:
        reproductionsInProcess = AnimalRepoduction.objects.filter(
            animal=animal,
            finished_date__isnull=True)

        for reproductionInProcess in reproductionsInProcess:
            if has_execution_type_before_specified_days(reproductionInProcess, execution_days):
                reproduction_count += 1
            if has_execution_before_specified_days(reproductionInProcess, revision_days):
                reproduction_count += 1
            if has_revision_before_specified_days(reproductionInProcess, separation_days):
                reproduction_count += 1
            if has_separation_before_specified_days(reproductionInProcess, give_birth_days):
                reproduction_count += 1

    return reproduction_count


def count_reproduction_process_on_danger(animals):
    danger_amount = 0
    execution_days = ReproductionProcessDays.EXECUTION.value
    revision_days = ReproductionProcessDays.REVISION.value
    separation_days = ReproductionProcessDays.SEPARATION.value
    give_birth_days = ReproductionProcessDays.GIVE_BIRTH.value
    for animal in animals:
        reproductionsInProcess = AnimalRepoduction.objects.filter(
            animal=animal,
            finished_date__isnull=True)

        for reproductionInProcess in reproductionsInProcess:
            if has_execution_type_after_specified_days(reproductionInProcess, execution_days):
                danger_amount += 1
            if has_execution_after_specified_days(reproductionInProcess, revision_days):
                danger_amount += 1
            if has_revision_after_specified_days(reproductionInProcess, separation_days):
                danger_amount += 1
            if has_separation_after_specified_days(reproductionInProcess, give_birth_days):
                danger_amount += 1

    return danger_amount


def has_execution_type_before_specified_days(reproductionInProcess, days):
    if reproductionInProcess.reproduction.preparation_date and not reproductionInProcess.reproduction.execution_date:
        diff = datetime.now().date() - reproductionInProcess.reproduction.preparation_date.date()
        return not diff.days > days


def has_execution_before_specified_days(reproductionInProcess, days):
    if reproductionInProcess.reproduction.execution_date and not reproductionInProcess.reproduction.revision_date:
        diff = datetime.now().date() - reproductionInProcess.reproduction.execution_date.date()
        return not diff.days > days


def has_revision_before_specified_days(reproductionInProcess, days):
    if reproductionInProcess.reproduction.revision_date and not reproductionInProcess.reproduction.separation_date:
        diff = datetime.now().date() - reproductionInProcess.reproduction.revision_date.date()
        return not diff.days > days


def has_separation_before_specified_days(reproductionInProcess, days):
    if reproductionInProcess.reproduction.separation_date and not reproductionInProcess.reproduction.give_birth_date:
        diff = datetime.now().date() - reproductionInProcess.reproduction.separation_date.date()
        return not diff.days > days


def has_execution_type_after_specified_days(reproductionInProcess, days):
    if reproductionInProcess.reproduction.preparation_date and not reproductionInProcess.reproduction.execution_date:
        diff = datetime.now().date() - reproductionInProcess.reproduction.preparation_date.date()
        return diff.days > days
    else:
        return False


def has_execution_after_specified_days(reproductionInProcess, days):
    if reproductionInProcess.reproduction.execution_date and not reproductionInProcess.reproduction.revision_date:
        diff = datetime.now().date() - reproductionInProcess.reproduction.execution_date.date()
        return diff.days > days


def has_revision_after_specified_days(reproductionInProcess, days):
    if reproductionInProcess.reproduction.revision_date and not reproductionInProcess.reproduction.separation_date:
        diff = datetime.now().date() - reproductionInProcess.reproduction.revision_date.date()
        return diff.days > days


def has_separation_after_specified_days(reproductionInProcess, days):
    if reproductionInProcess.reproduction.separation_date and not reproductionInProcess.reproduction.give_birth_date:
        diff = datetime.now().date() - reproductionInProcess.reproduction.separation_date.date()
        return diff.days > days


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
