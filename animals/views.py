from .models import (
    Animals,
    AnimalRepoduction,
    AcquisitionType,
    AnimalType,
    AnimalSanitary,
    AnimalDiet
)
from breedingcows.models import BreedingCows
from breedingcows.views import (
    get_reproductions_process_on_time,
    get_weaning_on_time,
    get_animals_without_reproduction_in_process_on_time,
    get_reproductions_process_warning,
    get_weaning_warning,
    get_animals_without_reproduction_in_process_warning,
    get_reproductions_process_on_danger,
    get_weaning_on_danger,
    get_animals_without_reproduction,
)
from reproduction.models import ReproductionProcessDays
from diets.models import Diet
from reproduction.forms import ReproductionForm
from sanitarybook.models import Sanitary
from django.shortcuts import render, get_object_or_404, redirect
from .forms import (
    AnimalForm,
    AnimalDietForm,
    AnimalRepoductionForm,
    PatherAnimalForm,
    WearningAnimalForm,
    AnimalSanitaryForm,
    AnimalPalpitationForm,
)
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
from django.core.paginator import Paginator
from datetime import timedelta
from predictions.models import Inputs
from predictions.views import predict
from datetime import date, datetime


@csrf_exempt
def animal_detail(request, pk):
    animal = get_object_or_404(Animals, pk=pk)
    animalDiet, animalReproduction, animalSanitary = getAnimalInfo(animal)
    successful, unsuccessful = getReproductionInfo(animal)

    return render(
        request,
        'animals/animal_detail.html',
        {
            'animal': animal,
            'animalReproduction': animalReproduction.first(),
            'animalDiets': animalDiet,
            'animalSanitaries': animalSanitary,
            'successfulInsemination': successful[0],
            'unsuccessfulInsemination': unsuccessful[0],
            'successfulNatural': successful[1],
            'unsuccessfulNatural': unsuccessful[1],
            'mother': Animals.get_mother(animal),
            'father': Animals.get_father(animal)
        }
    )


def animal_edit(request, pk):
    animal = get_object_or_404(Animals, pk=pk)

    if request.method == "POST":
        form = AnimalForm(request.POST, instance=animal)
        if form.is_valid():
            animal = form.save(commit=False)
            animal.save()
            return redirect('animal_detail', pk=animal.pk)
    else:
        form = AnimalForm(instance=animal)
    return render(request, 'animals/animal_edit.html', {'form': form})


def animal_new(request, breedingCowsPk):
    if request.method == "POST":
        animalForm = AnimalForm(request.POST, prefix="animalForm")
        if animalForm.is_valid():
            breedingCows = get_object_or_404(BreedingCows, pk=breedingCowsPk)
            animal = animalForm.save(commit=False)
            animal.breeding_cows = breedingCows
            animal.save()

        if isInsemination(animal.acquisition) or isNatural(animal.acquisition):
            motherAnimalForm = PatherAnimalForm(
                request.POST,
                breeding_cow=breedingCows,
                animal_type="Vaca",
                prefix="motherAnimalForm"
            )
            if motherAnimalForm.is_valid():
                motherId = (motherAnimalForm.cleaned_data['animal'].id)
                mother = get_object_or_404(Animals, pk=motherId)
                mother.brood.add(animal)
                mother.save()

        if isNatural(animal.acquisition):
            fatherAnimalForm = PatherAnimalForm(
                request.POST,
                breeding_cow=breedingCows,
                animal_type="Toro",
                prefix="fatherAnimalForm"
            )
            if fatherAnimalForm.is_valid():
                fatherId = (fatherAnimalForm.cleaned_data['animal'].id)
                father = get_object_or_404(Animals, pk=fatherId)
                father.brood.add(animal)
                father.save()

        return redirect('animal_detail', pk=animal.pk)
    else:
        breedingCows = get_object_or_404(BreedingCows, pk=breedingCowsPk)
        form = AnimalForm(prefix="animalForm")
        motherForm = PatherAnimalForm(
            breeding_cow=breedingCows,
            animal_type="Vaca",
            prefix="motherAnimalForm"
        )
        fatherForm = PatherAnimalForm(
            breeding_cow=breedingCows,
            animal_type="Toro",
            prefix="fatherAnimalForm"
        )
        return render(request, 'animals/animal_edit.html', {
            'breeding_cow': breedingCowsPk,
            'form': form,
            'formMother': motherForm,
            'formFather': fatherForm
        })


@csrf_exempt
def animal_diet_new(request, breedingCowsPk):
    if request.method == "POST":
        animal = get_object_or_404(Animals, id=request.POST['idAnimal'])
        diet = get_object_or_404(Diet, id=request.POST['idDiet'])
        animalDietForm = AnimalDietForm()
        animalDiet = animalDietForm.save(commit=False)
        animalDiet.animal = animal
        animalDiet.diet = diet
        animalDiet.diagnosis_date = timezone.now()
        animalDiet.save()

    breedingCows = get_object_or_404(BreedingCows, pk=breedingCowsPk)
    animals = Animals.objects.order_by(
        'flock_number'
    ).filter(
        breeding_cows=breedingCows,
        leaving_date__isnull=True
    )
    diets = Diet.objects.filter(
        delete_date__isnull=True,
    ).order_by(
        'name'
    )
    return render(
        request,
        'animals/animal_diet_new.html',
        {'animals': animals, 'breeding_cow': breedingCows, 'diets': diets}
    )


@csrf_exempt
def animal_palpation_new(request, breedingCowsPk):
    success = None
    if request.method == "POST":
        animal = get_object_or_404(Animals, id=request.POST['idAnimal'])
        sexualMaturity = request.POST['sexualMaturity']
        bodyDevelopment = request.POST['bodyDevelopment']
        disease = request.POST['disease']
        diseaseDescription = request.POST['diseaseDescription']

        animal.sexual_maturity = isPositive(sexualMaturity)
        animal.body_development = bodyDevelopment
        animal.disease = isPositive(disease)
        if isPositive(disease):
            animal.disease_description = diseaseDescription
        else:
            animal.disease_description = ""

        animal.save()
        success = True

    breedingCows = get_object_or_404(BreedingCows, pk=breedingCowsPk)
    form = AnimalPalpitationForm()
    animals = Animals.objects.order_by('flock_number').filter(
        breeding_cows=breedingCows,
        leaving_date__isnull=True
    ).exclude(
        animal_type="Toro"
    ).exclude(
        animal_type="Ternero"
    )
    return render(request, 'animals/animal_palpation_new.html', {
        'animals': animals,
        'breeding_cow': breedingCows,
        'form': form,
        'success': success
    })


def animal_weaning_new(request, breedingCowsPk):
    if request.method == "POST":
        form = WearningAnimalForm(
            request.POST,
            breeding_cow=breedingCowsPk,
            animal_type="Ternero",
        )
        if form.is_valid():
            animalId = (form.cleaned_data['animals'].id)
            animal = get_object_or_404(Animals, pk=animalId)
            animal.flock_number = form.cleaned_data['flock_number']
            sexType = form.cleaned_data['sex_type']
            if isFemale(sexType):
                animal.animal_type = AnimalType.VAQUILLONA.value
            else:
                animal.animal_type = AnimalType.TORO.value
            animal.save()

            sanitaryId = (form.cleaned_data['sanitary_books'].id)
            sanitary = get_object_or_404(Sanitary, id=sanitaryId)

            animalSanitaryForm = AnimalSanitaryForm()
            animalSanitary = animalSanitaryForm.save(commit=False)
            animalSanitary.animal = animal
            animalSanitary.sanitary = sanitary
            animalSanitary.done_date = timezone.now()
            animalSanitary.save()

    breedingCows = get_object_or_404(BreedingCows, pk=breedingCowsPk)
    nextAnimalToWeaning = Animals.objects.all().order_by(
        'entry_date'
    ).filter(
        breeding_cows=breedingCows,
        animal_type="Ternero",
        leaving_date__isnull=True
    ).first()
    if nextAnimalToWeaning:
        newForm = WearningAnimalForm(
            breeding_cow=breedingCows,
            animal_type="Ternero",
            initial={'animals': nextAnimalToWeaning.pk}
        )
    else:
        newForm = WearningAnimalForm(
            breeding_cow=breedingCows,
            animal_type="Ternero",
        )
    return render(
        request,
        'animals/animal_weaning_new.html',
        {'breeding_cow': breedingCows, 'form': newForm}
    )


@csrf_exempt
def animal_reproduction_type_new(request, breedingCowsPk):
    if request.method == "POST":
        animal = get_object_or_404(Animals, id=request.POST['idAnimal'])
        reproductionForm = ReproductionForm()
        reproduction = reproductionForm.save(commit=False)
        animalRepoductionForm = AnimalRepoductionForm()
        animalRepoduction = animalRepoductionForm.save(commit=False)

        reproduction.reproduction_type = request.POST['idReproduction']
        reproduction.has_prostaglandin_vaccine = isTrue(
            request.POST['has_prostaglandin_vaccine']
        )
        reproduction.has_vaginal_device = isTrue(
            request.POST['has_vaginal_device']
        )
        reproduction.preparation_date = parse_date(
            request.POST['execution_date']
        )
        if reproduction.preparation_date is None:
            reproduction.preparation_date = timezone.now()
        days = timedelta(days=ReproductionProcessDays.EXECUTION.value)
        reproduction.next_date = reproduction.preparation_date + days
        reproduction.save()

        animalRepoduction.reproduction = reproduction
        animalRepoduction.animal = animal
        animalRepoduction.started_date = reproduction.preparation_date
        animalRepoduction.breeding_cow = animal.breeding_cows
        animalRepoduction.save()

    breedingCows = get_object_or_404(BreedingCows, pk=breedingCowsPk)
    animals = getFemaleAnimalsWithoutReproductionInProcess(breedingCows)
    return render(
        request,
        'animals/animal_reproduction_type_new.html',
        {
            'animals': animals,
            'breeding_cow': breedingCows,
            'time': timezone.now
        }
    )


@csrf_exempt
def animal_reproduction_execution_new(request, breedingCowsPk):
    if request.method == "POST":
        animal = get_object_or_404(Animals, id=request.POST['idAnimal'])
        animalReproduction = AnimalRepoduction.objects.filter(
            animal=animal,
            finished_date__isnull=True
        ).first()

        reproduction = animalReproduction.reproduction
        reproduction.execution_date = parse_date(
            request.POST['executionDate']
        )
        if reproduction.execution_date is None:
            reproduction.execution_date = timezone.now()
        days = timedelta(days=ReproductionProcessDays.REVISION.value)
        reproduction.next_date = reproduction.execution_date + days
        reproduction.save()

    breedingCows = get_object_or_404(BreedingCows, pk=breedingCowsPk)
    animals = getFemaleAnimalsWithoutReproductionExecution(breedingCows)
    return render(
        request,
        'animals/animal_reproduction_execution_new.html',
        {
            'animals': animals,
            'breeding_cow': breedingCows,
            'time': timezone.now
        }
    )


@csrf_exempt
def animal_reproduction_revision_new(request, breedingCowsPk):
    if request.method == "POST":
        animal = get_object_or_404(Animals, id=request.POST['idAnimal'])
        result = request.POST['idResult']
        potentialGiveBirthDate = request.POST['potentialGiveBirthDate']
        animalReproduction = AnimalRepoduction.objects.filter(
            animal=animal,
            finished_date__isnull=True
        ).first()

        reproduction = animalReproduction.reproduction
        reproduction.revision_date = timezone.now()
        reproduction.success_revision = isPositive(result)
        if isPositive(result):
            reproduction.potential_give_birth_date = parse_date(
                potentialGiveBirthDate
            )
        else:
            animalReproduction.finished_date = timezone.now()
            animalReproduction.save()
        reproduction.revision_date = parse_date(
            request.POST['executionDate']
        )
        if reproduction.revision_date is None:
            reproduction.revision_date = timezone.now()
        if reproduction.potential_give_birth_date is None:
            reproduction.potential_give_birth_date = timezone.now()
        days = timedelta(days=ReproductionProcessDays.SEPARATION.value)
        reproduction.next_date = reproduction.revision_date + days
        reproduction.save()

    breedingCows = get_object_or_404(BreedingCows, pk=breedingCowsPk)
    animals = getFemaleAnimalsWithoutRevisionExecution(breedingCows)
    return render(
        request,
        'animals/animal_reproduction_revision_new.html',
        {
            'animals': animals,
            'breeding_cow': breedingCows,
            'time': timezone.now
        }
    )


@csrf_exempt
def animal_reproduction_separation_new(request, breedingCowsPk):
    if request.method == "POST":
        animal = get_object_or_404(Animals, id=request.POST['idAnimal'])
        animalReproduction = AnimalRepoduction.objects.filter(
            animal=animal,
            finished_date__isnull=True
        ).first()

        reproduction = animalReproduction.reproduction
        reproduction.separation_date = parse_date(
            request.POST['executionDate']
        )
        if reproduction.separation_date is None:
            reproduction.separation_date = timezone.now()
        reproduction.next_date = reproduction.potential_give_birth_date
        reproduction.save()

    breedingCows = get_object_or_404(BreedingCows, pk=breedingCowsPk)
    diets = Diet.objects.order_by('name')
    animals = getFemaleAnimalsWithoutSeparationExecution(breedingCows)
    return render(
        request,
        'animals/animal_reproduction_separation_new.html',
        {
            'animals': animals,
            'breeding_cow': breedingCows,
            'time': timezone.now,
            'diets': diets
        }
    )


@csrf_exempt
def animal_reproduction_success_new(request, breedingCowsPk):
    if request.method == "POST":
        animal = get_object_or_404(Animals, id=request.POST['idAnimal'])
        result = request.POST['idResult']
        animalReproduction = AnimalRepoduction.objects.filter(
            animal=animal,
            finished_date__isnull=True
        ).first()

        if animal.animal_type == "Vaquillona":
            animal.animal_type = "Vaca"
            animal.save()

        animalReproduction.finished_date = parse_date(
            request.POST['executionDate']
        )
        if animalReproduction.finished_date is None:
            animalReproduction.finished_date = timezone.now()
        animalReproduction.save()

        reproduction = animalReproduction.reproduction
        if isPositive(result):
            reproduction.give_birth_date = animalReproduction.finished_date
        reproduction.save()

    breedingCows = get_object_or_404(BreedingCows, pk=breedingCowsPk)
    animals = getFemaleAnimalsWithReproductionExecution(breedingCows)
    return render(
        request,
        'animals/animal_reproduction_success_new.html',
        {
            'animals': animals,
            'breeding_cow': breedingCows,
            'time': timezone.now
        }
    )


@csrf_exempt
def animal_rejected_new(request, breedingCowsPk):
    if request.method == "POST":
        animal = get_object_or_404(Animals, id=request.POST['idAnimal'])
        animal.rejection_date = parse_date(
            request.POST['executionDate']
        )
        if animal.rejection_date is None:
            animal.rejection_date = timezone.now()
        animal.save()

    potentialRejectedAnimals = []
    breedingCows = get_object_or_404(BreedingCows, pk=breedingCowsPk)
    animals = Animals.objects.all().order_by(
        'entry_date'
    ).filter(
        breeding_cows=breedingCows,
        rejection_date__isnull=True,
        leaving_date__isnull=True
    )
    for animal in animals:
        if hasPalpitationProblems(animal):
            potentialRejectedAnimals.append(animal)

        animalReproduction = AnimalRepoduction.objects.filter(
            animal=animal,
            finished_date__isnull=False
        ).first()

        if animalReproduction:
            if hasReproductionComplication(animalReproduction):
                if animal not in potentialRejectedAnimals:
                    potentialRejectedAnimals.append(animal)

    diets = Diet.objects.order_by('name')
    return render(
        request,
        'animals/animal_rejected_new.html',
        {
            'breeding_cow': breedingCows,
            'animals': potentialRejectedAnimals,
            'diets': diets,
            'time': timezone.now
        }
    )


@csrf_exempt
def animal_delete(request, breedingCowsPk):
    if request.method == "POST":
        animal = get_object_or_404(Animals, id=request.POST['idAnimal'])
        animal.leaving_date = parse_date(
            request.POST['executionDate']
        )
        if animal.leaving_date is None:
            animal.leaving_date = timezone.now()
        animal.save()

    breedingCows = get_object_or_404(BreedingCows, pk=breedingCowsPk)
    animals = Animals.objects.all().order_by(
        'entry_date'
    ).filter(
        breeding_cows=breedingCows,
        leaving_date__isnull=True,
    )

    return render(
        request,
        'animals/animal_delete.html',
        {
            'breeding_cow': breedingCows,
            'animals': animals,
            'time': timezone.now
        }
    )


def animals_list(request, breedingCowsPk, animalType):
    breedingCows = get_object_or_404(BreedingCows, pk=breedingCowsPk)
    animalInfo = []
    animals = Animals.objects.all().order_by(
        'flock_number'
    ).filter(
        breeding_cows=breedingCows,
        leaving_date__isnull=True,
        animal_type=animalType
    )

    for animal in animals:
        animalDiet, animalReproduction, animalSanitary = getAnimalInfo(animal)
        animalInfo.append([
            animal,
            animalDiet.last(),
            animalReproduction.first(),
            animalSanitary.last()
        ])

    paginator = Paginator(animalInfo, 7)
    page = request.GET.get('page')
    animalsInfoPaginated = paginator.get_page(page)

    return render(
        request,
        'animals/animals_list.html',
        {
            'breeding_cow': breedingCows,
            'animals': animalsInfoPaginated,
            'animal_type': animalType
        }
    )


@csrf_exempt
def animal_sanitary_new(request, breedingCowsPk):
    if request.method == "POST":
        animal = get_object_or_404(Animals, id=request.POST['idAnimal'])
        sanitary = get_object_or_404(Sanitary, id=request.POST['idSanitary'])

        animalSanitaryForm = AnimalSanitaryForm()
        animalSanitary = animalSanitaryForm.save(commit=False)
        animalSanitary.animal = animal
        animalSanitary.sanitary = sanitary
        animalSanitary.done_date = timezone.now()
        animalSanitary.save()

    breedingCows = get_object_or_404(BreedingCows, pk=breedingCowsPk)
    animals = Animals.objects.order_by(
        'flock_number'
    ).filter(
        breeding_cows=breedingCows,
        leaving_date__isnull=True
    )
    sanitaries = Sanitary.objects.filter(
        delete_date__isnull=True,
    ).order_by(
        'name'
    )
    return render(
        request,
        'animals/animal_sanitary_new.html',
        {
            'animals': animals,
            'breeding_cow': breedingCows,
            'sanitaries': sanitaries
        }
    )


def animal_on_time_process(request, breedingCowsPk):
    breedingCows = get_object_or_404(BreedingCows, pk=breedingCowsPk)
    animals = Animals.objects.order_by(
        'flock_number'
    ).filter(
        breeding_cows=breedingCows,
        leaving_date__isnull=True
    )
    reproduction_in_process = get_reproductions_process_on_time(animals)

    paginator = Paginator(reproduction_in_process, 5)
    page = request.GET.get('page')
    ReproductionInProcessPaginated = paginator.get_page(page)

    calfs_info = []
    calfs = get_weaning_on_time(breedingCowsPk)
    for calf in calfs:
        days = calf.birthday + timedelta(days=120)
        calfs_info.append([calf, days])

    paginator = Paginator(calfs_info, 5)
    page = request.GET.get('page')
    calfsInfoPaginated = paginator.get_page(page)

    animals_without_reproduction = get_animals_without_reproduction_in_process_on_time(animals)
    animals_without_reproduction_info = get_animals_info_on_time(animals_without_reproduction)

    paginator = Paginator(animals_without_reproduction_info, 5)
    page = request.GET.get('page')
    reproductionInfoPaginated = paginator.get_page(page)

    return render(
        request,
        'animals/animals_on_time_list.html',
        {
            'breeding_cow': breedingCows,
            'reproduction_in_process': ReproductionInProcessPaginated,
            'calfs_info': calfsInfoPaginated,
            'animals_without_reproduction_info': reproductionInfoPaginated
        }
    )


def get_animals_info_on_time(animals_without_reproduction):
    animals_without_reproduction_info = []
    for animal in animals_without_reproduction:
        if Animals.is_vaquillona(animal):
            days = animal.birthday + timedelta(days=730)
            animals_without_reproduction_info.append([animal, days])

        reproduction_finished = AnimalRepoduction.objects.filter(
            animal=animal,
            finished_date__isnull=False).order_by('-finished_date').first()

        if reproduction_finished is not None:
            days = reproduction_finished.finished_date + timedelta(
                days=ReproductionProcessDays.REPEAT_PROCESS.value
            )
            animals_without_reproduction_info.append([animal, days])

    return animals_without_reproduction_info


def animal_warning_process(request, breedingCowsPk):
    breedingCows = get_object_or_404(BreedingCows, pk=breedingCowsPk)
    animals = Animals.objects.order_by(
        'flock_number'
    ).filter(
        breeding_cows=breedingCows,
        leaving_date__isnull=True
    )
    reproduction_warning = get_reproductions_process_warning(animals)

    paginator = Paginator(reproduction_warning, 5)
    page = request.GET.get('page')
    ReproductionWarningPaginated = paginator.get_page(page)

    calfs_info = []
    calfs = get_weaning_warning(breedingCowsPk)
    for calf in calfs:
        days = calf.birthday + timedelta(days=120)
        calfs_info.append([calf, days])

    paginator = Paginator(calfs_info, 5)
    page = request.GET.get('page')
    calfsInfoPaginated = paginator.get_page(page)

    animals_without_reproduction = get_animals_without_reproduction_in_process_warning(animals)
    animals_without_reproduction_info = get_animals_info_warning(animals_without_reproduction)

    paginator = Paginator(animals_without_reproduction_info, 5)
    page = request.GET.get('page')
    reproductionInfoPaginated = paginator.get_page(page)

    return render(
        request,
        'animals/animals_warning_list.html',
        {
            'breeding_cow': breedingCows,
            'reproduction_warning': ReproductionWarningPaginated,
            'calfs_info': calfsInfoPaginated,
            'animals_without_reproduction': reproductionInfoPaginated
        }
    )


@csrf_exempt
def change_animal_weight(request, breedingCowsPk):
    if request.method == "POST":
        animal = get_object_or_404(Animals, id=request.POST['idAnimal'])
        animal.weight = request.POST['idWeight']
        animal.save()

    breedingCows = get_object_or_404(BreedingCows, pk=breedingCowsPk)
    animals = Animals.objects.order_by(
        'flock_number'
    ).filter(
        breeding_cows=breedingCows,
        leaving_date__isnull=True
    )
    return render(
        request,
        'animals/animal_weight.html',
        {
            'animals': animals,
            'breeding_cow': breedingCows,
        }
    )


@csrf_exempt
def undo_rejected_animal(request, breedingCowsPk):
    if request.method == "POST":
        animal = get_object_or_404(Animals, id=request.POST['idAnimal'])
        animal.leaving_date = None
        animal.save()

    breedingCows = get_object_or_404(BreedingCows, pk=breedingCowsPk)
    animals = Animals.objects.order_by(
        'flock_number'
    ).filter(
        breeding_cows=breedingCows,
        leaving_date__isnull=False
    )
    return render(
        request,
        'animals/animal_undo_rejected.html',
        {
            'animals': animals,
            'breeding_cow': breedingCows,
        }
    )


def get_animals_info_warning(animals_without_reproduction):
    animals_without_reproduction_info = []
    for animal in animals_without_reproduction:
        if Animals.is_vaquillona(animal):
            days = animal.birthday + timedelta(days=730)
            animals_without_reproduction_info.append([animal, days])

        reproduction_finished = AnimalRepoduction.objects.filter(
            animal=animal,
            finished_date__isnull=False).order_by('-finished_date').first()

        if reproduction_finished is not None:
            days = reproduction_finished.finished_date + timedelta(
                days=ReproductionProcessDays.REPEAT_PROCESS.value
            )
            animals_without_reproduction_info.append([animal, days])

    return animals_without_reproduction_info


def animal_on_danger_process(request, breedingCowsPk):
    breedingCows = get_object_or_404(BreedingCows, pk=breedingCowsPk)
    animals = Animals.objects.order_by(
        'flock_number'
    ).filter(
        breeding_cows=breedingCows,
        leaving_date__isnull=True
    )
    reproduction_on_danger = get_reproductions_process_on_danger(animals)

    paginator = Paginator(reproduction_on_danger, 5)
    page = request.GET.get('page')
    ReproductionOnDangerPaginated = paginator.get_page(page)

    calfs_info = []
    calfs = get_weaning_on_danger(breedingCowsPk)
    for calf in calfs:
        days = calf.birthday + timedelta(days=120)
        calfs_info.append([calf, days])

    paginator = Paginator(calfs_info, 5)
    page = request.GET.get('page')
    calfsInfoPaginated = paginator.get_page(page)

    animals_without_reproduction = get_animals_without_reproduction(animals)
    animals_without_reproduction_info = []
    for animal in animals_without_reproduction:
        if Animals.is_vaca(animal):
            animals_without_reproduction_info.append([animal, animal.birthday])
        else:
            days = animal.birthday + timedelta(days=730)
            animals_without_reproduction_info.append([animal, days])

    paginator = Paginator(animals_without_reproduction_info, 5)
    page = request.GET.get('page')
    reproductionInfoPaginated = paginator.get_page(page)

    return render(
        request,
        'animals/animals_on_danger_list.html',
        {
            'breeding_cow': breedingCows,
            'reproduction_on_danger': ReproductionOnDangerPaginated,
            'calfs_info': calfsInfoPaginated,
            'animals_without_reproduction_info': reproductionInfoPaginated
        }
    )


def animal_machine_learning_integration(request, breedingCowsPk):
    breedingCows = get_object_or_404(BreedingCows, pk=breedingCowsPk)
    femaleAnimals = getFemaleAnimalsWithoutReproductionInProcess(breedingCows)
    animalsInfo = []

    for animal in femaleAnimals:
        animalDiet, animalReproduction, animalSanitary = getAnimalInfo(animal)
        newInput = get_input_from_animal(animal)
        perduction = predict(newInput)
        animalsInfo.append([
            animal,
            animalDiet.last(),
            animalReproduction.first(),
            animalSanitary.last(),
            perduction
        ])

    paginator = Paginator(animalsInfo, 7)
    page = request.GET.get('page')
    animalsInfoPaginated = paginator.get_page(page)

    return render(
        request,
        'animals/animals_machine_learning_integration.html',
        {
            'breeding_cow': breedingCows,
            'female_animals': animalsInfoPaginated,
        }
    )


def get_input_from_animal(animal):
    newInput = Inputs
    newInput.age = Animals.get_age(animal)
    newInput.body_development = animal.body_development
    newInput.season = get_season(date.today())

    animalReproductions = AnimalRepoduction.objects.all().order_by(
        '-started_date'
    ).filter(
        animal=animal,
        finished_date__isnull=False
    )

    success_reproduction_count = 0
    fail_reproduction_count = 0
    pregnant_after_count = 0
    empty_after_count = 0

    for animalReproduction in animalReproductions:
        if animalReproduction.reproduction.give_birth_date is not None:
            success_reproduction_count += 1
        else:
            fail_reproduction_count += 1

        if animalReproduction.reproduction.success_revision:
            pregnant_after_count += 1
        else:
            empty_after_count += 1

    newInput.success_reproduction_count = success_reproduction_count
    newInput.fail_reproduction_count = fail_reproduction_count
    newInput.pregnant_after_count = pregnant_after_count
    newInput.empty_after_count = empty_after_count

    lastSuccessReproduction = getLastSuccessReproduction(animal)
    lastFailedReproduction = getLastFailedReproduction(animal)

    if lastSuccessReproduction is not None:
        newInput.days_from_last_success_reproduction = abs(
            date.today() - lastSuccessReproduction.started_date).days
    else:
        newInput.days_from_last_success_reproduction = 0

    if lastFailedReproduction is not None:
        newInput.days_from_last_fail_reproduction = abs(
            date.today() - lastFailedReproduction.started_date).days
    else:
        newInput.days_from_last_fail_reproduction = 0

    return newInput


def getAnimalInfo(animal):
    animalDiet = AnimalDiet.objects.all().order_by(
        'diagnosis_date'
    ).filter(
        animal=animal
    )
    animalReproduction = AnimalRepoduction.objects.all().order_by(
        '-started_date'
    ).filter(
        animal=animal
    )
    animalSanitary = AnimalSanitary.objects.all().order_by(
        'done_date'
    ).filter(
        animal=animal
    )

    return (
        animalDiet,
        animalReproduction,
        animalSanitary
    )


def getReproductionInfo(animal):
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


def isFemale(string):
    return string == "Hembra"


def isPositive(string):
    return string == "Positivo"


def isTrue(string):
    return string == "true"


def isInsemination(string):
    return string == AcquisitionType.INSEMINACION.value


def isNatural(string):
    return string == AcquisitionType.NATURAL.value


def hasPalpitationProblems(animal):
    print(animal.body_development)
    if hasPalpitationValuesComplete(animal):
        return not animal.sexual_maturity or animal.body_development == 0 or animal.disease
    else:
        return False


def hasPalpitationValuesComplete(animal):
    return animal.sexual_maturity is not None and animal.body_development != 0 and animal.disease is not None


def hasReproductionComplication(animalReproduction):
    return animalReproduction.reproduction.give_birth_date is None


def getFemaleAnimals(breedingCows):
    return Animals.objects.order_by(
        'flock_number'
    ).filter(
        breeding_cows=breedingCows,
        leaving_date__isnull=True,
        sexual_maturity=True,
        disease=False
    ).exclude(
        animal_type='Toro'
    ).exclude(
        animal_type='Ternero'
    ).exclude(
        body_development=0
    )


def getFemaleAnimalsWithoutReproductionInProcess(breedingcows):
    femaleAnimals = getFemaleAnimals(breedingcows)
    reproductionsInProcess = AnimalRepoduction.objects.filter(
        breeding_cow=breedingcows,
        finished_date__isnull=True)

    for reproductionInProcess in reproductionsInProcess:
        femaleAnimals = femaleAnimals.exclude(
            flock_number=reproductionInProcess.animal.flock_number)

    return femaleAnimals


def getFemaleAnimalsWithoutReproductionExecution(breedingcows):
    femaleAnimals = []
    reproductionsInProcess = AnimalRepoduction.objects.filter(
        breeding_cow=breedingcows,
        finished_date__isnull=True)

    for reproductionInProcess in reproductionsInProcess:
        if not reproductionInProcess.reproduction.execution_date and not reproductionInProcess.animal.leaving_date:
            femaleAnimals.append(reproductionInProcess.animal)

    return femaleAnimals


def getFemaleAnimalsWithoutRevisionExecution(breedingcows):
    femaleAnimals = []
    reproductionsInProcess = AnimalRepoduction.objects.filter(
        breeding_cow=breedingcows,
        finished_date__isnull=True)

    for reproductionInProcess in reproductionsInProcess:
        if not reproductionInProcess.reproduction.revision_date and reproductionInProcess.reproduction.execution_date and not reproductionInProcess.animal.leaving_date:
            femaleAnimals.append(reproductionInProcess.animal)

    return femaleAnimals


def getFemaleAnimalsWithoutSeparationExecution(breedingcows):
    femaleAnimals = []
    reproductionsInProcess = AnimalRepoduction.objects.filter(
        breeding_cow=breedingcows,
        finished_date__isnull=True)

    for reproductionInProcess in reproductionsInProcess:
        if not reproductionInProcess.reproduction.separation_date and reproductionInProcess.reproduction.revision_date and not reproductionInProcess.animal.leaving_date:
            femaleAnimals.append(reproductionInProcess.animal)

    return femaleAnimals


def getFemaleAnimalsWithReproductionExecution(breedingcows):
    femaleAnimals = []
    reproductionsInProcess = AnimalRepoduction.objects.filter(
        breeding_cow=breedingcows,
        finished_date__isnull=True)

    for reproductionInProcess in reproductionsInProcess:
        femaleAnimals.append(reproductionInProcess.animal)

    return femaleAnimals


def getLastSuccessReproduction(animal):
    animalReproductions = AnimalRepoduction.objects.all().order_by(
        '-started_date'
    ).filter(
        animal=animal,
        finished_date__isnull=False
    )

    for animalReproduction in animalReproductions:
        if animalReproduction.reproduction.give_birth_date is not None:
            return animalReproduction


def getLastFailedReproduction(animal):
    animalReproductions = AnimalRepoduction.objects.all().order_by(
        '-started_date'
    ).filter(
        animal=animal,
        finished_date__isnull=False
    )

    for animalReproduction in animalReproductions:
        if animalReproduction.reproduction.give_birth_date is None:
            return animalReproduction


def get_season(now):
    Y = 2021

    seasons = [(4, (date(Y, 1, 1), date(Y, 3, 20))),
               (1, (date(Y, 3, 21), date(Y, 6, 20))),
               (2, (date(Y, 6, 21), date(Y, 9, 22))),
               (3, (date(Y, 9, 23), date(Y, 12, 20))),
               (4, (date(Y, 12, 21), date(Y, 12, 31)))]

    if isinstance(now, datetime):
        now = now.date()
    now = now.replace(year=Y)
    return next(season for season, (start, end) in seasons
                if start <= now <= end)
