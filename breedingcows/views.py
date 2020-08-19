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
from operator import attrgetter
from django.contrib.auth.decorators import login_required


@login_required
def breeding_cows_list(request):
    breeding_cows_all = BreedingCows.objects.filter(
        leaving_date__isnull=True,
    ).order_by(
        'entry_date'
    )
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

    on_time_amount = len(get_reproductions_process_on_time(animals))
    on_time_amount += len(get_weaning_on_time(pk))
    on_time_amount += len(get_animals_without_reproduction_in_process_on_time(animals))
    warning_amount = len(get_reproductions_process_warning(animals))
    warning_amount += len(get_weaning_warning(pk))
    warning_amount += len(get_animals_without_reproduction_in_process_warning(animals))
    danger_amount = len(get_reproductions_process_on_danger(animals))
    danger_amount += len(get_weaning_on_danger(pk))
    danger_amount += len(get_animals_without_reproduction(animals))

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

    return render(
        request,
        'breedingcows/breeding_cow_notification.html',
        {
            'breeding_cow': breeding_cow
        }
    )


def get_reproductions_process_on_time(animals):
    on_time_list = []
    for animal in animals:
        reproductionInProcess = AnimalRepoduction.objects.filter(
            animal=animal,
            finished_date__isnull=True).first()
        if reproductionInProcess:
            if has_reproduction_in_process_on_time(reproductionInProcess):
                on_time_list.append(reproductionInProcess)

    on_time_list = sorted(
        on_time_list,
        key=attrgetter('reproduction.next_date')
    )
    return on_time_list


def has_reproduction_in_process_on_time(reproductionInProcess):
    return (has_execution_type_before_next_date(
        reproductionInProcess.reproduction
    ) or has_execution_before_next_date(
        reproductionInProcess.reproduction
    ) or has_revision_before_next_date(
        reproductionInProcess.reproduction
    ) or has_separation_before_next_date(
        reproductionInProcess.reproduction
    ))


def get_animals_without_reproduction_in_process_on_time(animals):
    on_time_list = []

    for animal in animals:
        reproductionInProcess = AnimalRepoduction.objects.filter(
            animal=animal,
            finished_date__isnull=True).first()
        lastReproductionProcessed = AnimalRepoduction.objects.filter(
            animal=animal,
            finished_date__isnull=False).order_by('-finished_date').first()
        if has_not_reproduction_in_process_on_time(
                reproductionInProcess,
                lastReproductionProcessed,
                animal
        ):
            on_time_list.append(animal)

    on_time_list = sorted(
        on_time_list,
        key=attrgetter('birthday')
    )

    return on_time_list


def has_not_reproduction_in_process_on_time(reproductionInProcess, lastReproductionProcessed, animal):
    finished_reproduction_days = ReproductionProcessDays.REPEAT_PROCESS.value
    became_vaquillona_days = 720

    if reproductionInProcess:
        return False

    if lastReproductionProcessed:
        return has_finished_redroduction_before_specified_days(
            lastReproductionProcessed,
            finished_reproduction_days
        )
    if animal.animal_type == AnimalType.VAQUILLONA.value:
        return has_become_vaquillona_before_specified_days(
            animal,
            became_vaquillona_days
        )

    return False


def get_reproductions_process_warning(animals):
    warning_list = []

    for animal in animals:
        reproductionInProcess = AnimalRepoduction.objects.filter(
            animal=animal,
            finished_date__isnull=True).first()
        if reproductionInProcess:
            if has_reproduction_in_process_warning(reproductionInProcess):
                warning_list.append(reproductionInProcess)

    return warning_list


def get_animals_without_reproduction_in_process_warning(animals):
    warning_list = []

    for animal in animals:
        reproductionInProcess = AnimalRepoduction.objects.filter(
            animal=animal,
            finished_date__isnull=True).first()
        lastReproductionProcessed = AnimalRepoduction.objects.filter(
            animal=animal,
            finished_date__isnull=False).order_by('-finished_date').first()
        if has_no_reproduction_in_process_warning(
                reproductionInProcess,
                lastReproductionProcessed,
                animal
        ):
            warning_list.append(animal)

    warning_list = sorted(
        warning_list,
        key=attrgetter('birthday')
    )

    return warning_list


def has_reproduction_in_process_warning(reproductionInProcess):
    return (
            has_execution_type_in_same_specified_days(
                reproductionInProcess.reproduction
            ) or has_execution_in_same_specified_days(
        reproductionInProcess.reproduction
    ) or has_revision_in_same_specified_days(
        reproductionInProcess.reproduction
    ) or has_separation_in_same_specified_days(
        reproductionInProcess.reproduction
    )
    )


def has_no_reproduction_in_process_warning(reproductionInProcess, lastReproductionProcessed, animal):
    finished_reproduction_days = ReproductionProcessDays.REPEAT_PROCESS.value
    became_vaquillona_days = 730

    if reproductionInProcess:
        return False

    if lastReproductionProcessed:
        return has_finished_redroduction_in_same_specified_days(
            lastReproductionProcessed,
            finished_reproduction_days
        )
    if animal.animal_type == AnimalType.VAQUILLONA.value:
        return has_become_vaquillona_in_same_specified_days(
            animal,
            became_vaquillona_days
        )

    return False


def get_reproductions_process_on_danger(animals):
    danger_list = []

    for animal in animals:
        reproductionInProcess = AnimalRepoduction.objects.filter(
            animal=animal,
            finished_date__isnull=True).first()
        lastReproductionProcessed = AnimalRepoduction.objects.filter(
            animal=animal,
            finished_date__isnull=False).order_by('-finished_date').first()
        if reproductionInProcess:
            if has_reproduction_in_process_on_danger(reproductionInProcess.reproduction):
                danger_list.append(reproductionInProcess)
        else:
            if has_no_reproduction_in_process_on_danger(
                    lastReproductionProcessed,
                    animal
            ):
                danger_list.append(lastReproductionProcessed)

    return danger_list


def has_reproduction_in_process_on_danger(reproductionInProcess):
    return (
            has_execution_type_after_specified_days(
                reproductionInProcess
            ) or has_execution_after_specified_days(
        reproductionInProcess
    ) or has_revision_after_specified_days(
        reproductionInProcess
    ) or has_separation_after_specified_days(
        reproductionInProcess
    )
    )


def has_no_reproduction_in_process_on_danger(lastReproductionProcessed, animal):
    finished_reproduction_days = ReproductionProcessDays.REPEAT_PROCESS.value

    if lastReproductionProcessed:
        return has_finished_redroduction_after_specified_days(
            lastReproductionProcessed,
            finished_reproduction_days
        )

    return False


def get_animals_without_reproduction(animals):
    danger_list = []
    became_vaquillona_days = 730

    for animal in animals:
        reproductionInProcess = AnimalRepoduction.objects.filter(
            animal=animal,
            finished_date__isnull=True).first()
        lastReproductionProcessed = AnimalRepoduction.objects.filter(
            animal=animal,
            finished_date__isnull=False).order_by('-finished_date').first()
        if not reproductionInProcess and not lastReproductionProcessed:
            if animal.animal_type == AnimalType.VACA.value:
                danger_list.append(animal)
            if animal.animal_type == AnimalType.VAQUILLONA.value:
                if has_become_vaquillona_after_specified_days(
                        animal,
                        became_vaquillona_days
                ):
                    danger_list.append(animal)

    return danger_list


def get_weaning_on_time(breeding_cow):
    on_time_list = []
    weaning_days = 120

    terneros = Animals.objects.filter(
        breeding_cows=breeding_cow,
        animal_type=AnimalType.TERNERO.value,
        rejection_date__isnull=True,
        leaving_date__isnull=True
    )

    for ternero in terneros:
        if has_born_before_specified_days(ternero, weaning_days):
            on_time_list.append(ternero)

    on_time_list = sorted(
        on_time_list,
        key=attrgetter('birthday')
    )

    return on_time_list


def get_weaning_warning(breeding_cow):
    weaning_list = []
    weaning_days = 120

    terneros = Animals.objects.filter(
        breeding_cows=breeding_cow,
        animal_type=AnimalType.TERNERO.value,
        rejection_date__isnull=True,
        leaving_date__isnull=True
    )

    for ternero in terneros:
        if has_born_in_same_specified_days(ternero, weaning_days):
            weaning_list.append(ternero)

    return weaning_list


def get_weaning_on_danger(breeding_cow):
    weaning_on_danger_list = []
    weaning_days = 120

    terneros = Animals.objects.filter(
        breeding_cows=breeding_cow,
        animal_type=AnimalType.TERNERO.value,
        rejection_date__isnull=True,
        leaving_date__isnull=True
    )

    for ternero in terneros:
        if has_born_after_specified_days(ternero, weaning_days):
            weaning_on_danger_list.append(ternero)

    return weaning_on_danger_list


def has_execution_type_before_next_date(reproductionInProcess):
    if (
            reproductionInProcess.preparation_date and not
    reproductionInProcess.execution_date
    ):
        return datetime.now().date() < reproductionInProcess.next_date


def has_execution_before_next_date(reproductionInProcess):
    if (
            reproductionInProcess.execution_date and not
    reproductionInProcess.revision_date
    ):
        return datetime.now().date() < reproductionInProcess.next_date


def has_revision_before_next_date(reproductionInProcess):
    if (
            reproductionInProcess.revision_date and not
    reproductionInProcess.separation_date
    ):
        return datetime.now().date() < reproductionInProcess.next_date


def has_separation_before_next_date(reproductionInProcess):
    if (
            reproductionInProcess.separation_date and not
    reproductionInProcess.give_birth_date
    ):
        return datetime.now().date() < reproductionInProcess.next_date


def has_execution_type_in_same_specified_days(reproductionInProcess):
    if (
            reproductionInProcess.preparation_date and not
    reproductionInProcess.execution_date
    ):
        return datetime.now().date() == reproductionInProcess.next_date


def has_execution_in_same_specified_days(reproductionInProcess):
    if (
            reproductionInProcess.execution_date and not
    reproductionInProcess.revision_date
    ):
        return datetime.now().date() == reproductionInProcess.next_date


def has_revision_in_same_specified_days(reproductionInProcess):
    if (
            reproductionInProcess.revision_date and not
    reproductionInProcess.separation_date
    ):
        return datetime.now().date() == reproductionInProcess.next_date


def has_separation_in_same_specified_days(reproductionInProcess):
    if (
            reproductionInProcess.separation_date and not
    reproductionInProcess.give_birth_date
    ):
        return datetime.now().date() == reproductionInProcess.next_date


def has_execution_type_after_specified_days(reproductionInProcess):
    if (
            reproductionInProcess.preparation_date and not
    reproductionInProcess.execution_date
    ):
        return datetime.now().date() > reproductionInProcess.next_date


def has_execution_after_specified_days(reproductionInProcess):
    if (
            reproductionInProcess.execution_date and not
    reproductionInProcess.revision_date
    ):
        return datetime.now().date() > reproductionInProcess.next_date


def has_revision_after_specified_days(reproductionInProcess):
    if (
            reproductionInProcess.revision_date and not
    reproductionInProcess.separation_date
    ):
        return datetime.now().date() > reproductionInProcess.next_date


def has_separation_after_specified_days(reproductionInProcess):
    if (
            reproductionInProcess.separation_date and not
    reproductionInProcess.give_birth_date
    ):
        return datetime.now().date() > reproductionInProcess.next_date


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
        breeding_cows_address = BreedingCows.objects.filter(
            leaving_date__isnull=True
        ).order_by(
            'entry_date'
        ).values_list(
            'address',
            flat=True
        )

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
            breeding_cows_animal_count.append(
                Animals.objects.all().filter(breeding_cows=breeding_cow, leaving_date__isnull=True).count())
            breeding_cows_vacas_count.append(
                Animals.objects.all().filter(breeding_cows=breeding_cow, animal_type="Vaca",
                                             leaving_date__isnull=True).count())
            breeding_cows_ternero_count.append(
                Animals.objects.all().filter(breeding_cows=breeding_cow, animal_type="Ternero",
                                             leaving_date__isnull=True).count())
            breeding_cows_vaquillonas_count.append(
                Animals.objects.all().filter(breeding_cows=breeding_cow, animal_type="Vaquillona",
                                             leaving_date__isnull=True).count())
            breeding_cows_toros_count.append(
                Animals.objects.all().filter(breeding_cows=breeding_cow, animal_type="Toro",
                                             leaving_date__isnull=True).count())

            vacas_count = vacas_count + Animals.objects.all().filter(breeding_cows=breeding_cow, animal_type="Vaca",
                                                                     leaving_date__isnull=True).count()
            ternero_count = ternero_count + Animals.objects.all().filter(breeding_cows=breeding_cow,
                                                                         animal_type="Ternero",
                                                                         leaving_date__isnull=True).count()
            vaquillonas_count = vaquillonas_count + Animals.objects.all().filter(breeding_cows=breeding_cow,
                                                                                 animal_type="Vaquillona",
                                                                                 leaving_date__isnull=True).count()
            toros_count = toros_count + Animals.objects.all().filter(breeding_cows=breeding_cow, animal_type="Toro",
                                                                     leaving_date__isnull=True).count()

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
