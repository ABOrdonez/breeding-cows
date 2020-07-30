from .models import (
    Animals,
    AnimalRepoduction,
    AcquisitionType,
    AnimalType,
    AnimalSanitary,
    AnimalDiet
)
from breedingcows.models import BreedingCows
from reproduction.models import Reproduction
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
    ReproductionProcessDays
)
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


@csrf_exempt
def animal_detail(request, pk):
    animal = get_object_or_404(Animals, pk=pk)
    animalDiet, animalReproduction, animalSanitary = getAnimalInfo(animal)
    return render(
        request,
        'animals/animal_detail.html',
        {
            'animal': animal,
            'animalReproduction': animalReproduction,
            'animalDiet': animalDiet,
            'animalSanitary': animalSanitary
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
    diets = Diet.objects.order_by('name')
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
        animal.body_development = isPositive(bodyDevelopment)
        animal.disease = isPositive(disease)
        if isPositive(disease):
            animal.disease_description = diseaseDescription

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
        animalRepoduction.started_date = timezone.now()
        animalRepoduction.breeding_cow = animal.breeding_cows
        animalRepoduction.save()

    breedingCows = get_object_or_404(BreedingCows, pk=breedingCowsPk)
    animals = getFemaleAnimalsWithoutReproductionInProcess(breedingCows)
    return render(
        request,
        'animals/animal_reproduction_type_new.html',
        {'animals': animals, 'breeding_cow': breedingCows}
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
        {'animals': animals, 'breeding_cow': breedingCows}
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
        {'animals': animals, 'breeding_cow': breedingCows}
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
        days = timedelta(days=ReproductionProcessDays.GIVE_BIRTH.value)
        reproduction.next_date = reproduction.separation_date + days
        reproduction.save()

    breedingCows = get_object_or_404(BreedingCows, pk=breedingCowsPk)
    diets = Diet.objects.order_by('name')
    animals = getFemaleAnimalsWithoutSeparationExecution(breedingCows)
    return render(
        request,
        'animals/animal_reproduction_separation_new.html',
        {'animals': animals, 'breeding_cow': breedingCows, 'diets': diets}
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
        {'animals': animals, 'breeding_cow': breedingCows}
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

    diets = Diet.objects.order_by('name')
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
                if not animal in potentialRejectedAnimals:
                    potentialRejectedAnimals.append(animal)

    return render(
        request,
        'animals/animal_rejected_new.html',
        {
            'breeding_cow': breedingCows,
            'animals': potentialRejectedAnimals,
            'diets': diets
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
            'animals': animals
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
            animalDiet,
            animalReproduction,
            animalSanitary
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
    sanitaries = Sanitary.objects.order_by('name')
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
        if animal.animal_type == AnimalType.VAQUILLONA.value:
            days = animal.birthday + timedelta(days=730)
            animals_without_reproduction_info.append([animal, days])

        reproduction_finished = AnimalRepoduction.objects.filter(
            animal=animal,
            finished_date__isnull=False).order_by('-finished_date').first()

        if not reproduction_finished is None:
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
    print(animals_without_reproduction_info)

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


def get_animals_info_warning(animals_without_reproduction):
    animals_without_reproduction_info = []
    for animal in animals_without_reproduction:
        if animal.animal_type == AnimalType.VAQUILLONA.value:
            days = animal.birthday + timedelta(days=730)
            animals_without_reproduction_info.append([animal, days])

        reproduction_finished = AnimalRepoduction.objects.filter(
            animal=animal,
            finished_date__isnull=False).order_by('-finished_date').first()

        if not reproduction_finished is None:
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
        if animal.animal_type == AnimalType.VACA.value:
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


def getAnimalInfo(animal):
    animalDiet = AnimalDiet.objects.all().order_by(
        '-diagnosis_date'
    ).filter(
        animal=animal
    ).first()
    animalReproduction = AnimalRepoduction.objects.all().order_by(
        '-started_date'
    ).filter(
        animal=animal
    ).first()
    animalSanitary = AnimalSanitary.objects.all().order_by(
        '-done_date'
    ).filter(
        animal=animal
    ).first()

    return (
        animalDiet,
        animalReproduction,
        animalSanitary
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
    if hasPalpitationValuesComplete(animal):
        return not animal.sexual_maturity or not animal.body_development or animal.disease
    else:
        return False


def hasPalpitationValuesComplete(animal):
    return animal.sexual_maturity is not None and animal.body_development is not None and animal.disease is not None


def hasReproductionComplication(animalReproduction):
    return animalReproduction.reproduction.give_birth_date is None


def getFemaleAnimals(breedingCows):
    return Animals.objects.order_by(
        'flock_number'
    ).filter(
        breeding_cows=breedingCows,
        leaving_date__isnull=True
    ).exclude(
        animal_type='Toro'
    ).exclude(
        animal_type='Ternero'
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
