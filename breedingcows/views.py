from .models import BreedingCows
from animals.models import Animals, AnimalType, AnimalRepoduction
from django.shortcuts import render, get_object_or_404
from .forms import BreedingCowForm
from django.shortcuts import redirect
from django.core.paginator import Paginator
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from reproduction.models import Reproduction
from operator import attrgetter
from django.contrib.auth.decorators import login_required
import datetime
from django.utils import timezone


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
        {'breeding_cows': breeding_cows_pagenated}
    )


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

    return render(
        request,
        'breedingcows/breeding_cow_detail.html',
        {
            'breeding_cow': breeding_cow,
            'animals': animals_info,
            'on_time_amount': on_time_amount,
            'warning_amount': warning_amount,
            'danger_amount': danger_amount
        }
    )


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
        return render(
            request,
            'breedingcows/breeding_cow_edit.html',
            {'form': form}
        )


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

    return render(
        request,
        'breedingcows/breeding_cow_edit.html',
        {'form': form}
    )


def breeding_cow_delete(request, pk):
    breeding_cow = get_object_or_404(BreedingCows, pk=pk)
    BreedingCows.add_leaving_date(breeding_cow)

    return redirect('breeding_cows_list')


def breeding_cow_notification(request, pk, notification_type):
    breeding_cow = get_object_or_404(BreedingCows, pk=pk)

    return render(
        request,
        'breedingcows/breeding_cow_notification.html',
        {'breeding_cow': breeding_cow}
    )


def get_reproductions_process_on_time(animals):
    on_time_list = []
    for animal in animals:
        reproductionInProcess = AnimalRepoduction.objects.filter(
            animal=animal,
            finished_date__isnull=True).first()
        if reproductionInProcess:
            if has_reproduction_in_process_on_time(reproductionInProcess.reproduction):
                on_time_list.append(reproductionInProcess)

    on_time_list = sorted(
        on_time_list,
        key=attrgetter('reproduction.next_date')
    )
    return on_time_list


def has_reproduction_in_process_on_time(reproduction):
    return (Reproduction.has_execution_type_before_next_date(
        reproduction
    ) or Reproduction.has_execution_before_next_date(
        reproduction
    ) or Reproduction.has_revision_before_next_date(
        reproduction
    ) or Reproduction.has_separation_before_next_date(
        reproduction
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
    if reproductionInProcess:
        return False

    if lastReproductionProcessed:
        return AnimalRepoduction.has_finished_before_expected_days(
            lastReproductionProcessed,
        )

    if Animals.is_vaquillona(animal):
        return Animals.has_become_vaquillona_before_expected_days(
            animal
        )

    return False


def get_reproductions_process_warning(animals):
    warning_list = []

    for animal in animals:
        reproductionInProcess = AnimalRepoduction.objects.filter(
            animal=animal,
            finished_date__isnull=True).first()
        if reproductionInProcess:
            if has_reproduction_in_process_warning(reproductionInProcess.reproduction):
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


def has_reproduction_in_process_warning(reproduction):
    return (Reproduction.has_execution_type_in_same_specified_days(
        reproduction
    ) or Reproduction.has_execution_in_same_specified_days(
        reproduction
    ) or Reproduction.has_revision_in_same_specified_days(
        reproduction
    ) or Reproduction.has_separation_in_same_specified_days(
        reproduction
    ))


def has_no_reproduction_in_process_warning(reproductionInProcess, lastReproductionProcessed, animal):
    if reproductionInProcess:
        return False

    if lastReproductionProcessed:
        return AnimalRepoduction.has_finished_in_same_expected_days(
            lastReproductionProcessed,
        )
    if Animals.is_vaquillona(animal):
        return Animals.has_become_vaquillona_in_same_expected_days(
            animal
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


def has_reproduction_in_process_on_danger(reproduction):
    return (Reproduction.has_execution_type_after_specified_days(
        reproduction
    ) or Reproduction.has_execution_after_specified_days(
        reproduction
    ) or Reproduction.has_revision_after_specified_days(
        reproduction
    ) or Reproduction.has_separation_after_specified_days(
        reproduction
    ))


def has_no_reproduction_in_process_on_danger(lastReproductionProcessed, animal):
    if lastReproductionProcessed:
        return AnimalRepoduction.has_finished_after_expected_days(
            lastReproductionProcessed,
        )

    return False


def get_animals_without_reproduction(animals):
    danger_list = []

    for animal in animals:
        reproductionInProcess = AnimalRepoduction.objects.filter(
            animal=animal,
            finished_date__isnull=True).first()
        lastReproductionProcessed = AnimalRepoduction.objects.filter(
            animal=animal,
            finished_date__isnull=False).order_by('-finished_date').first()
        if not reproductionInProcess and not lastReproductionProcessed:
            if Animals.is_vaca(animal):
                danger_list.append(animal)
            if Animals.is_vaquillona(animal):
                if Animals.has_become_vaquillona_after_expected_days(
                        animal
                ):
                    danger_list.append(animal)

    return danger_list


def get_weaning_on_time(breeding_cow):
    on_time_list = []

    terneros = Animals.objects.filter(
        breeding_cows=breeding_cow,
        animal_type=AnimalType.TERNERO.value,
        rejection_date__isnull=True,
        leaving_date__isnull=True
    )

    for ternero in terneros:
        if Animals.has_born_before_expected_days(ternero):
            on_time_list.append(ternero)

    on_time_list = sorted(
        on_time_list,
        key=attrgetter('birthday')
    )

    return on_time_list


def get_weaning_warning(breeding_cow):
    weaning_list = []

    terneros = Animals.objects.filter(
        breeding_cows=breeding_cow,
        animal_type=AnimalType.TERNERO.value,
        rejection_date__isnull=True,
        leaving_date__isnull=True
    )

    for ternero in terneros:
        if Animals.has_born_in_same_expected_days(ternero):
            weaning_list.append(ternero)

    return weaning_list


def get_weaning_on_danger(breeding_cow):
    weaning_on_danger_list = []

    terneros = Animals.objects.filter(
        breeding_cows=breeding_cow,
        animal_type=AnimalType.TERNERO.value,
        rejection_date__isnull=True,
        leaving_date__isnull=True
    )

    for ternero in terneros:
        if Animals.has_born_after_expected_days(ternero):
            weaning_on_danger_list.append(ternero)

    return weaning_on_danger_list


def breeding_cow_dashboard(request, pk):
    breedingCow = get_object_or_404(BreedingCows, pk=pk)
    animals = Animals.objects.all().filter(
        breeding_cows=pk,
        leaving_date__isnull=True
    )
    vacas = Animals.objects.all().filter(
        breeding_cows=pk,
        leaving_date__isnull=True,
        animal_type=AnimalType.VACA.value
    )
    terneros = Animals.objects.all().filter(
        breeding_cows=pk,
        leaving_date__isnull=True,
        animal_type=AnimalType.TERNERO.value
    )
    vaquillonas = Animals.objects.all().filter(
        breeding_cows=pk,
        leaving_date__isnull=True,
        animal_type=AnimalType.VAQUILLONA.value
    )
    toros = Animals.objects.all().filter(
        breeding_cows=pk,
        leaving_date__isnull=True,
        animal_type=AnimalType.TORO.value
    )

    vacas_insemination = [0, 0]
    vacas_natural = [0, 0]
    vacas_insemination_last_year = [0, 0]
    vacas_natural_last_year = [0, 0]

    on_time_amount = len(get_reproductions_process_on_time(animals))
    warning_amount = len(get_reproductions_process_warning(animals))
    danger_amount = len(get_reproductions_process_on_danger(animals))

    sexual_maturity_count = 0
    body_development_count = 0
    disease_count = 0
    kilograms = 0

    animals_types = [
        AnimalType.VACA.value,
        AnimalType.TERNERO.value,
        AnimalType.VAQUILLONA.value,
        AnimalType.TORO.value
    ]

    animals_count_by_types = [
        len(vacas),
        len(terneros),
        len(vaquillonas),
        len(toros),
    ]

    reproductions_in_process_animals_types = [
        AnimalType.VACA.value,
        AnimalType.VAQUILLONA.value,
    ]

    reproductions_in_process = [0, 0]

    for vaca in vacas:
        successful, unsuccessful = getReproductionInfo(vaca, False)
        vacas_insemination[0] += successful[0]
        vacas_natural[0] += successful[1]
        vacas_insemination[1] += unsuccessful[0]
        vacas_natural[1] += unsuccessful[1]

        successfulLastYear, unsuccessfulLastYear = getReproductionInfo(
            vaca,
            True)
        vacas_insemination_last_year[0] += successfulLastYear[0]
        vacas_natural_last_year[0] += successfulLastYear[1]
        vacas_insemination_last_year[1] += unsuccessfulLastYear[0]
        vacas_natural_last_year[1] += unsuccessfulLastYear[1]

        reproduction_in_process = AnimalRepoduction.objects.filter(
            animal=vaca,
            finished_date__isnull=True,
        ).first()
        if reproduction_in_process:
            reproductions_in_process[0] += 1

    for vaquillona in vaquillonas:
        reproduction_in_process = AnimalRepoduction.objects.filter(
            animal=vaquillona,
            finished_date__isnull=True,
        ).first()

        if reproduction_in_process:
            reproductions_in_process[1] += 1

    for animal in animals:
        kilograms += animal.weight
        if animal.sexual_maturity:
            sexual_maturity_count += 1
        if animal.body_development:
            body_development_count += 1
        if animal.disease:
            disease_count += 1

    data = {
        "animals_types": animals_types,
        "animals_count_by_types": animals_count_by_types,
        "animals_count": len(animals),
        "kilograms": kilograms,
        "reproductions_in_process_animals_types":
        reproductions_in_process_animals_types,
        "reproductions_in_process": reproductions_in_process,
        "vacas_insemination": vacas_insemination,
        'vacas_natural': vacas_natural,
        "vacas_insemination_last_year": vacas_insemination_last_year,
        "vacas_natural_last_year": vacas_natural_last_year,
        "on_time_amount": on_time_amount,
        "warning_amount": warning_amount,
        'danger_amount': danger_amount,
        'sexual_maturity_count': sexual_maturity_count,
        'body_development_count': body_development_count,
        'disease_count': disease_count,
    }

    return render(
        request,
        'breedingcows/breeding_cow_bashboard.html',
        {
            'breeding_cow': breedingCow,
            'data': data
        }
    )


def getReproductionInfo(animal, isfromLastYear):
    if isfromLastYear:
        animalReproductions = AnimalRepoduction.objects.all().order_by(
            '-started_date'
        ).filter(
            animal=animal,
            started_date__gte=datetime.datetime(
                timezone.now().year,
                1,
                1)
        )
    else:
        animalReproductions = AnimalRepoduction.objects.all().order_by(
            '-started_date'
        ).filter(
            animal=animal
        )

    successfulReproductions = [0, 0]
    unsuccessfulReproductions = [0, 0]

    for reproduction in animalReproductions:
        if reproduction.finished_date:
            if reproduction.reproduction.give_birth_date:
                if reproduction.reproduction.reproduction_type == 'Inseminacion Artificial A Tiempos Fijos':
                    successfulReproductions[0] += 1
                else:
                    successfulReproductions[1] += 1
            else:
                if reproduction.reproduction.reproduction_type == 'Inseminacion Artificial A Tiempos Fijos':
                    unsuccessfulReproductions[0] += 1
                else:
                    unsuccessfulReproductions[1] += 1
    return (
        successfulReproductions,
        unsuccessfulReproductions,
    )


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
