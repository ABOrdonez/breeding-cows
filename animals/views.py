from .models import (
    Animals,
    AnimalRepoduction,
    AcquisitionType,
    AnimalType,
    AnimalSanitary
)
from breedingcows.models import BreedingCows
from reproduction.models import Reproduction
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
from breedingcows.views import breeding_cow_detail
from django.utils.dateparse import parse_date


def animals_list(request):
    animals = Animals.objects.order_by('flock_number')
    return render(request, 'animals/animals_list.html', {'animals': animals})


@csrf_exempt
def animal_detail(request, pk):
    animal = get_object_or_404(Animals, pk=pk)
    return render(request, 'animals/animal_detail.html', {'animal': animal})


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
        print(request.POST['idDiet'])
        animal = get_object_or_404(Animals, id=request.POST['idAnimal'])
        diet = get_object_or_404(Diet, id=request.POST['idDiet'])
        print(diet)
        animalDietForm = AnimalDietForm()
        animalDiet = animalDietForm.save(commit=False)
        animalDiet.animal = animal
        animalDiet.diet = diet
        animalDiet.diagnosis_date = timezone.now()
        animalDiet.save()

    breedingCows = get_object_or_404(BreedingCows, pk=breedingCowsPk)
    animals = Animals.objects.order_by('flock_number').filter(
        breeding_cows=breedingCows)
    diets = Diet.objects.order_by('name')
    return render(request, 'animals/animal_diet_new.html', {
        'animals': animals,
        'breeding_cow': breedingCows,
        'diets': diets}
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
        breeding_cows=breedingCows
    ).exclude(
        animal_type="Toro"
    ).exclude(
        animal_type="Ternero")
    return render(request, 'animals/animal_palpation_new.html', {
        'animals': animals,
        'breeding_cow': breedingCows,
        'form': form,
        'success': success}
    )


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
        animal_type="Ternero"
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
    return render(request, 'animals/animal_weaning_new.html', {
        'breeding_cow': breedingCows,
        'form': newForm}
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
        reproduction.preparation_date = timezone.now()
        reproduction.save()

        animalRepoduction.reproduction = reproduction
        animalRepoduction.animal = animal
        animalRepoduction.started_date = timezone.now()
        animalRepoduction.breeding_cow = animal.breeding_cows
        animalRepoduction.save()

        return breeding_cow_detail(request, pk=animal.pk)

    else:
        breedingCows = get_object_or_404(BreedingCows, pk=breedingCowsPk)
        animals = getFemaleAnimalsWithoutReproductionInProcess(breedingCows)
        return render(request, 'animals/animal_reproduction_type_new.html', {
            'animals': animals,
            'breeding_cow': breedingCows,
        })


@csrf_exempt
def animal_reproduction_execution_new(request, breedingCowsPk):
    if request.method == "POST":
        animal = get_object_or_404(Animals, id=request.POST['idAnimal'])
        animalReproductions = AnimalRepoduction.objects.filter(
            animal=animal,
            finished_date__isnull=True)

        for animalReproduction in animalReproductions:
            reproduction = animalReproduction.reproduction
            reproduction.execution_date = timezone.now()
            reproduction.save()

        return breeding_cow_detail(request, pk=animal.pk)

    else:
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
        if not isPositive(result):
            animalReproduction.finished_date = timezone.now()
            animalReproduction.save()
        else:
            reproduction.potential_give_birth_date = parse_date(
                potentialGiveBirthDate
            )

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
        reproduction.separation_date = timezone.now()
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
        animalReproductions = AnimalRepoduction.objects.filter(
            animal=animal,
            finished_date__isnull=True)

        if animal.animal_type == "Vaquillona":
            animal.animal_type = "Vaca"
            animal.save()

        for animalReproduction in animalReproductions:
            animalReproduction.finished_date = timezone.now()
            reproduction = animalReproduction.reproduction
            if isSuccess(result):
                reproduction.give_birth_date = timezone.now()
            reproduction.save()
            animalReproduction.save()

        return breeding_cow_detail(request, pk=animal.pk)

    else:
        breedingCows = get_object_or_404(BreedingCows, pk=breedingCowsPk)
        animals = getFemaleAnimalsWithReproductionExecution(breedingCows)
        return render(request, 'animals/animal_reproduction_success_new.html', {'animals': animals, 'breeding_cow': breedingCows})


def isAceptable(string):
    return string == "Aceptable"


def isContiene(string):
    return string == "Contiene"


def isFemale(string):
    return string == "Hembra"


def isPositive(string):
    return string == "Positivo"


def isSuccess(string):
    return string == "Éxitoso"


def isTrue(string):
    return string == "true"


def isInsemination(string):
    return string == AcquisitionType.INSEMINACION.value


def isNatural(string):
    return string == AcquisitionType.NATURAL.value


def getFemaleAnimals(breedingCows):
    return Animals.objects.order_by('flock_number').filter(breeding_cows=breedingCows).exclude(animal_type='Toro').exclude(animal_type='Ternero')


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
        if not reproductionInProcess.reproduction.execution_date:
            femaleAnimals.append(reproductionInProcess.animal)

    return femaleAnimals


def getFemaleAnimalsWithoutRevisionExecution(breedingcows):
    femaleAnimals = []
    reproductionsInProcess = AnimalRepoduction.objects.filter(
        breeding_cow=breedingcows,
        finished_date__isnull=True)

    for reproductionInProcess in reproductionsInProcess:
        if not reproductionInProcess.reproduction.revision_date and reproductionInProcess.reproduction.execution_date:
            femaleAnimals.append(reproductionInProcess.animal)

    return femaleAnimals


def getFemaleAnimalsWithoutSeparationExecution(breedingcows):
    femaleAnimals = []
    reproductionsInProcess = AnimalRepoduction.objects.filter(
        breeding_cow=breedingcows,
        finished_date__isnull=True)

    for reproductionInProcess in reproductionsInProcess:
        if not reproductionInProcess.reproduction.separation_date and reproductionInProcess.reproduction.revision_date:
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
