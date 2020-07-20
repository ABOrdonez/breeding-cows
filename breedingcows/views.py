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
            breeding_cows=breeding_cow,
            leaving_date__isnull=True
        ).count()])

    paginator = Paginator(breeding_cows, 4)
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

    on_time_amount = count_reproductions_process_on_time(animals)
    on_time_amount += count_weaning_on_time(pk)
    warning_amount = count_reproductions_process_warning(animals)
    warning_amount += count_weaning_warning(pk)
    danger_amount = count_reproductions_process_on_danger(animals)
    danger_amount += count_weaning_on_danger(pk)

    return render(request, 'breedingcows/breeding_cow_detail.html', {
        'breeding_cow': breeding_cow,
        'animals': animals_info,
        'on_time_amount': on_time_amount,
        'warning_amount': warning_amount,
        'danger_amount': danger_amount})


def breeding_cow_new(request):
    if request.method == "POST":
        form = BreedingCowForm(request.POST)
        if form.is_valid():
            breeding_cow = form.save(commit=False)
            breeding_cow.owner = request.user
            breeding_cow.save()
            return redirect('breeding_cow_detail', pk=breeding_cow.pk)
    else:
        form = BreedingCowForm()
        return render(request, 'breedingcows/breeding_cow_edit.html', {
            'form': form})


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

    return render(request, 'breedingcows/breeding_cow_edit.html', {
        'form': form})


def breeding_cow_delete(request, pk):
    breeding_cow = get_object_or_404(BreedingCows, pk=pk)
    BreedingCows.add_leaving_date(breeding_cow)

    return redirect('breeding_cows_list')


def breeding_cow_notification(request, pk, notification_type):
    breeding_cow = get_object_or_404(BreedingCows, pk=pk)


    return render(request, 'breedingcows/breeding_cow_notification.html', {
        'breeding_cow': breeding_cow})


def count_reproductions_process_on_time(animals):
    on_time_count = 0

    for animal in animals:
        reproductionInProcess = AnimalRepoduction.objects.filter(
            animal=animal,
            finished_date__isnull=True).first()
        lastReproductionProcessed = AnimalRepoduction.objects.filter(
            animal=animal,
            finished_date__isnull=False).order_by('-finished_date').first()
        if reproductionInProcess:
            on_time_count += get_count_reproduction_in_process_on_time(reproductionInProcess)
        else:
            on_time_count += get_count_no_reproduction_in_process_on_time(lastReproductionProcessed, animal)

    return on_time_count


def get_count_reproduction_in_process_on_time(reproductionInProcess):
    on_time_count = 0
    execution_days = ReproductionProcessDays.EXECUTION.value
    revision_days = ReproductionProcessDays.REVISION.value
    separation_days = ReproductionProcessDays.SEPARATION.value
    give_birth_days = ReproductionProcessDays.GIVE_BIRTH.value

    if has_execution_type_before_specified_days(reproductionInProcess, execution_days):
        on_time_count += 1
    if has_execution_before_specified_days(reproductionInProcess, revision_days):
        on_time_count += 1
    if has_revision_before_specified_days(reproductionInProcess, separation_days):
        on_time_count += 1
    if has_separation_before_specified_days(reproductionInProcess, give_birth_days):
        on_time_count += 1

    return on_time_count


def get_count_no_reproduction_in_process_on_time(lastReproductionProcessed, animal):
    on_time_count = 0
    finished_reproduction_days = ReproductionProcessDays.REPEAT_PROCESS.value
    became_vaquillona_days = 730

    if lastReproductionProcessed:
        if has_finished_redroduction_before_specified_days(lastReproductionProcessed, finished_reproduction_days):
            on_time_count += 1
    if animal.animal_type == AnimalType.VAQUILLONA.value:
        if has_become_vaquillona_before_specified_days(animal, became_vaquillona_days):
            on_time_count += 1

    return on_time_count


def count_reproductions_process_warning(animals):
    warning_count = 0

    for animal in animals:
        reproductionInProcess = AnimalRepoduction.objects.filter(
            animal=animal,
            finished_date__isnull=True).first()
        lastReproductionProcessed = AnimalRepoduction.objects.filter(
            animal=animal,
            finished_date__isnull=False).order_by('-finished_date').first()
        if reproductionInProcess:
            warning_count += get_count_reproduction_in_process_warning(reproductionInProcess)
        else:
            warning_count += get_count_no_reproduction_in_process_warning(lastReproductionProcessed, animal)

    return warning_count


def get_count_reproduction_in_process_warning(reproductionInProcess):
    warning_count = 0
    execution_days = ReproductionProcessDays.EXECUTION.value
    revision_days = ReproductionProcessDays.REVISION.value
    separation_days = ReproductionProcessDays.SEPARATION.value
    give_birth_days = ReproductionProcessDays.GIVE_BIRTH.value

    if has_execution_type_in_same_specified_days(reproductionInProcess, execution_days):
        warning_count += 1
    if has_execution_in_same_specified_days(reproductionInProcess, revision_days):
        warning_count += 1
    if has_revision_in_same_specified_days(reproductionInProcess, separation_days):
        warning_count += 1
    if has_separation_in_same_specified_days(reproductionInProcess, give_birth_days):
        warning_count += 1

    return warning_count

def get_count_no_reproduction_in_process_warning(lastReproductionProcessed, animal):
    warning_count = 0
    finished_reproduction_days = ReproductionProcessDays.REPEAT_PROCESS.value
    became_vaquillona_days = 730

    if lastReproductionProcessed:
        if has_finished_redroduction_in_same_specified_days(lastReproductionProcessed, finished_reproduction_days):
            warning_count += 1
    if animal.animal_type == AnimalType.VAQUILLONA.value:
        if has_become_vaquillona_in_same_specified_days(animal, became_vaquillona_days):
            warning_count += 1

    return warning_count


def count_reproductions_process_on_danger(animals):
    danger_amount = 0

    for animal in animals:
        reproductionInProcess = AnimalRepoduction.objects.filter(
            animal=animal,
            finished_date__isnull=True).first()
        lastReproductionProcessed = AnimalRepoduction.objects.filter(
            animal=animal,
            finished_date__isnull=False).order_by('-finished_date').first()
        if reproductionInProcess:
            danger_amount += get_count_reproduction_in_process_on_danger(reproductionInProcess)
        else:
            danger_amount += get_count_no_reproduction_in_process_on_danger(lastReproductionProcessed, animal)
    
    return danger_amount


def get_count_reproduction_in_process_on_danger(reproductionInProcess):
    danger_amount = 0
    execution_days = ReproductionProcessDays.EXECUTION.value
    revision_days = ReproductionProcessDays.REVISION.value
    separation_days = ReproductionProcessDays.SEPARATION.value
    give_birth_days = ReproductionProcessDays.GIVE_BIRTH.value

    if has_execution_type_after_specified_days(reproductionInProcess, execution_days):
        danger_amount += 1
    if has_execution_after_specified_days(reproductionInProcess, revision_days):
        danger_amount += 1
    if has_revision_after_specified_days(reproductionInProcess, separation_days):
        danger_amount += 1
    if has_separation_after_specified_days(reproductionInProcess, give_birth_days):
        danger_amount += 1

    return danger_amount


def get_count_no_reproduction_in_process_on_danger(lastReproductionProcessed, animal):
    danger_amount = 0
    finished_reproduction_days = ReproductionProcessDays.REPEAT_PROCESS.value
    became_vaquillona_days = 730

    if lastReproductionProcessed:
        if has_finished_redroduction_after_specified_days(lastReproductionProcessed, finished_reproduction_days):
            danger_amount += 1
    else:
        if animal.animal_type == AnimalType.VACA.value:
            danger_amount += 1
    if animal.animal_type == AnimalType.VAQUILLONA.value:
        if has_become_vaquillona_after_specified_days(animal, became_vaquillona_days):
            danger_amount += 1

    return danger_amount


def count_weaning_on_time(breeding_cow):
    on_time_count = 0
    weaning_days = 120

    terneros = Animals.objects.filter(
        breeding_cows=breeding_cow,
        animal_type=AnimalType.TERNERO.value,
        rejection_date__isnull=True,
        leaving_date__isnull=True
    )

    for ternero in terneros:
        if has_born_before_specified_days(ternero, weaning_days):
            on_time_count += 1

    return on_time_count


def count_weaning_warning(breeding_cow):
    weaning_count = 0
    weaning_days = 120

    terneros = Animals.objects.filter(
        breeding_cows=breeding_cow,
        animal_type=AnimalType.TERNERO.value,
        rejection_date__isnull=True,
        leaving_date__isnull=True
    )

    for ternero in terneros:
        if has_born_in_same_specified_days(ternero, weaning_days):
            weaning_count += 1

    return weaning_count


def count_weaning_on_danger(breeding_cow):
    weaning_on_danger_count = 0
    weaning_days = 120

    terneros = Animals.objects.filter(
        breeding_cows=breeding_cow,
        animal_type=AnimalType.TERNERO.value,
        rejection_date__isnull=True,
        leaving_date__isnull=True
    )

    for ternero in terneros:
        if has_born_after_specified_days(ternero, weaning_days):
            weaning_on_danger_count += 1

    return weaning_on_danger_count


def has_execution_type_before_specified_days(reproductionInProcess, days):
    if reproductionInProcess.reproduction.preparation_date and not reproductionInProcess.reproduction.execution_date:
        diff = datetime.now().date() - reproductionInProcess.reproduction.preparation_date
        return diff.days < days


def has_execution_before_specified_days(reproductionInProcess, days):
    if reproductionInProcess.reproduction.execution_date and not reproductionInProcess.reproduction.revision_date:
        diff = datetime.now().date() - reproductionInProcess.reproduction.execution_date
        return diff.days < days


def has_revision_before_specified_days(reproductionInProcess, days):
    if reproductionInProcess.reproduction.revision_date and not reproductionInProcess.reproduction.separation_date:
        diff = datetime.now().date() - reproductionInProcess.reproduction.revision_date
        return diff.days < days


def has_separation_before_specified_days(reproductionInProcess, days):
    if reproductionInProcess.reproduction.separation_date and not reproductionInProcess.reproduction.give_birth_date:
        diff = datetime.now().date() - reproductionInProcess.reproduction.separation_date
        return diff.days < days


def has_execution_type_in_same_specified_days(reproductionInProcess, days):
    if reproductionInProcess.reproduction.preparation_date and not reproductionInProcess.reproduction.execution_date:
        diff = datetime.now().date() - reproductionInProcess.reproduction.preparation_date
        return diff.days == days


def has_execution_in_same_specified_days(reproductionInProcess, days):
    if reproductionInProcess.reproduction.execution_date and not reproductionInProcess.reproduction.revision_date:
        diff = datetime.now().date() - reproductionInProcess.reproduction.execution_date
        return diff.days == days


def has_revision_in_same_specified_days(reproductionInProcess, days):
    if reproductionInProcess.reproduction.revision_date and not reproductionInProcess.reproduction.separation_date:
        diff = datetime.now().date() - reproductionInProcess.reproduction.revision_date
        return diff.days == days


def has_separation_in_same_specified_days(reproductionInProcess, days):
    if reproductionInProcess.reproduction.separation_date and not reproductionInProcess.reproduction.give_birth_date:
        diff = datetime.now().date() - reproductionInProcess.reproduction.separation_date
        return diff.days == days


def has_execution_type_after_specified_days(reproductionInProcess, days):
    if reproductionInProcess.reproduction.preparation_date and not reproductionInProcess.reproduction.execution_date:
        diff = datetime.now().date() - reproductionInProcess.reproduction.preparation_date
        return diff.days > days


def has_execution_after_specified_days(reproductionInProcess, days):
    if reproductionInProcess.reproduction.execution_date and not reproductionInProcess.reproduction.revision_date:
        diff = datetime.now().date() - reproductionInProcess.reproduction.execution_date
        return diff.days > days


def has_revision_after_specified_days(reproductionInProcess, days):
    if reproductionInProcess.reproduction.revision_date and not reproductionInProcess.reproduction.separation_date:
        diff = datetime.now().date() - reproductionInProcess.reproduction.revision_date
        return diff.days > days


def has_separation_after_specified_days(reproductionInProcess, days):
    if reproductionInProcess.reproduction.separation_date and not reproductionInProcess.reproduction.give_birth_date:
        diff = datetime.now().date() - reproductionInProcess.reproduction.separation_date
        return diff.days > days


def has_born_before_specified_days(animals, days):
    if animals.birthday:
        diff = datetime.now().date() - animals.birthday
        return diff.days < days


def has_born_after_specified_days(animals, days):
    if animals.birthday:
        diff = datetime.now().date() - animals.birthday
        return diff.days > days


def has_born_in_same_specified_days(animals, days):
    if animals.birthday:
        diff = datetime.now().date() - animals.birthday
        return diff.days == days


def has_finished_redroduction_before_specified_days(finishedReproduction, days):
    if finishedReproduction.finished_date:
        diff = datetime.now().date() - finishedReproduction.finished_date
        return diff.days < days


def has_finished_redroduction_after_specified_days(finishedReproduction, days):
    if finishedReproduction.finished_date:
        diff = datetime.now().date() - finishedReproduction.finished_date
        return diff.days > days


def has_finished_redroduction_in_same_specified_days(finishedReproduction, days):
    if finishedReproduction.finished_date:
        diff = datetime.now().date() - finishedReproduction.finished_date
        return diff.days == days


def has_become_vaquillona_before_specified_days(animal, days):
    if animal.birthday:
        diff = datetime.now().date() - animal.birthday
        return diff.days < days


def has_become_vaquillona_after_specified_days(animal, days):
    if animal.birthday:
        diff = datetime.now().date() - animal.birthday
        return diff.days > days


def has_become_vaquillona_in_same_specified_days(animal, days):
    if animal.birthday:
        diff = datetime.now().date() - animal.birthday
        return diff.days == days


class ChartData(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        breeding_cows_address = BreedingCows.objects.filter(leaving_date__isnull=True).order_by('entry_date').values_list('address', flat=True)

        breeding_cows_all = BreedingCows.objects.filter(leaving_date__isnull=True).order_by('entry_date')
        breeding_cows_animal_count = []
        breeding_cows_vacas_count = []
        breeding_cows_ternero_count = []
        breeding_cows_vaquillonas_count = []
        breeding_cows_toros_count = []
        breeding_cows_reproduction_in_process = []

        animals_types = ['Vaca', 'Ternero', 'Vaquillona', 'Toro']
        vacas_count = 0
        ternero_count = 0
        vaquillonas_count = 0
        toros_count = 0

        for breeding_cow in breeding_cows_all:
            animals = Animals.objects.all().filter(breeding_cows=breeding_cow, leaving_date__isnull=True)
            breeding_cows_animal_count.append(Animals.objects.all().filter(breeding_cows=breeding_cow, leaving_date__isnull=True).count())
            breeding_cows_vacas_count.append(Animals.objects.all().filter(breeding_cows=breeding_cow, animal_type="Vaca", leaving_date__isnull=True).count())
            breeding_cows_ternero_count.append(Animals.objects.all().filter(breeding_cows=breeding_cow, animal_type="Ternero", leaving_date__isnull=True).count())
            breeding_cows_vaquillonas_count.append(Animals.objects.all().filter(breeding_cows=breeding_cow, animal_type="Vaquillona", leaving_date__isnull=True).count())
            breeding_cows_toros_count.append(Animals.objects.all().filter(breeding_cows=breeding_cow, animal_type="Toro", leaving_date__isnull=True).count())

            vacas_count = vacas_count + Animals.objects.all().filter(breeding_cows=breeding_cow, animal_type="Vaca", leaving_date__isnull=True).count()
            ternero_count = ternero_count + Animals.objects.all().filter(breeding_cows=breeding_cow, animal_type="Ternero", leaving_date__isnull=True).count()
            vaquillonas_count = vaquillonas_count + Animals.objects.all().filter(breeding_cows=breeding_cow, animal_type="Vaquillona", leaving_date__isnull=True).count()
            toros_count = toros_count + Animals.objects.all().filter(breeding_cows=breeding_cow, animal_type="Toro", leaving_date__isnull=True).count()

            reproduction_in_process_count = 0
            for animal in animals:
                reproductionInProcess = AnimalRepoduction.objects.filter(
                    animal=animal,
                    finished_date__isnull=True).first()
                if reproductionInProcess:
                    reproduction_in_process_count += 1

            breeding_cows_reproduction_in_process.append(reproduction_in_process_count)

        data = {
            "breeding_cows": breeding_cows_address,
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
            "breeding_cows_reproduction_in_process": breeding_cows_reproduction_in_process,
        }
        return Response(data)
