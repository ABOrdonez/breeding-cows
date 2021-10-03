from django import forms
from .models import (
    Animals,
    AnimalDiet,
    AnimalRepoduction,
    AnimalType,
    AcquisitionType,
    sexType,
    AnimalSanitary,
    ReproductiveStatus,
)
from sanitarybook.models import Sanitary


class AnimalForm(forms.ModelForm):
    class Meta:
        model = Animals
        fields = (
            'flock_number',
            'entry_date',
            'weight',
            'birthday',
            'animal_type',
            'acquisition',
        )
        widgets = {
            'animal_type': forms.Select(
                choices=AnimalType,
                attrs={
                    'class': 'form-control',
                    'onchange': 'try_to_disable_flock_number();'
                }
            ),
            'acquisition': forms.Select(
                choices=AcquisitionType,
                attrs={
                    'class': 'form-control',
                    'onchange': 'try_to_disable_parents();'
                }
            ),
        }


class AnimalDietForm(forms.ModelForm):
    class Meta:
        model = AnimalDiet
        fields = (
            'animal',
            'diet',
        )


class AnimalSanitaryForm(forms.ModelForm):
    class Meta:
        model = AnimalSanitary
        fields = (
            'animal',
            'sanitary',
        )


class AnimalRepoductionForm(forms.ModelForm):
    class Meta:
        model = AnimalRepoduction
        fields = (
            'animal',
            'started_date',
            'reproduction',
            'finished_date'
        )


class WearningAnimalForm(forms.Form):
    def __init__(self, *args, **kwargs):
        breeding_cow = kwargs.pop('breeding_cow')
        animal_type = kwargs.pop('animal_type')
        super(WearningAnimalForm, self).__init__(*args, **kwargs)
        self.fields['animals'] = forms.ModelChoiceField(
            queryset=Animals.objects.all().order_by(
                'entry_date'
            ).filter(
                breeding_cows=breeding_cow,
                animal_type=animal_type,
                leaving_date__isnull=True
            ),
            required=True,
            help_text="Terneros",
            widget=CustomSelect(attrs={'class': 'form-control'})
        )

    flock_number = forms.IntegerField()
    sanitary_books = forms.ModelChoiceField(
        queryset=Sanitary.objects.all().order_by(
            'name'
        ),
        required=True,
        help_text="Libreta Sanitaria",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    sex_type = forms.ChoiceField(
        choices=sexType.choices,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class AnimalPalpitationForm(forms.Form):
    sexual_maturity = forms.ChoiceField(
        choices=ReproductiveStatus.choices,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    body_development = forms.IntegerField()

    disease = forms.ChoiceField(
        choices=ReproductiveStatus.choices,
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'onchange': 'try_to_disable_description();'
            }
        )
    )
    disease_description = forms.CharField(required=False)


class PatherAnimalForm(forms.Form):
    def __init__(self, *args, **kwargs):
        breeding_cow = kwargs.pop('breeding_cow')
        animal_type = kwargs.pop('animal_type')
        super(PatherAnimalForm, self).__init__(*args, **kwargs)
        self.fields['animal'] = forms.ModelChoiceField(
            queryset=Animals.objects.all().order_by(
                'flock_number'
            ).filter(
                breeding_cows=breeding_cow,
                animal_type=animal_type,
                leaving_date__isnull=True
            ),
            required=False,
            help_text="Padre",
            widget=CustomSelect(attrs={'class': 'form-control'})
        )


class CustomSelect(forms.Select):
    option_inherits_attrs = True
