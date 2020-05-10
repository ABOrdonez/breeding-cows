from django import forms
from .models import Animals, AnimalDiet, AnimalRepoduction


class AnimalForm(forms.ModelForm):
    class Meta:
        model = Animals
        fields = ('flock_number', 'entry_date', 'weight', 'birthday', 'animal_type',)


class AnimalDietForm(forms.ModelForm):
    class Meta:
        model = AnimalDiet
        fields = ('animal', 'diet',)


class AnimalRepoductionForm(forms.ModelForm):
    class Meta:
    	model = AnimalRepoduction
    	fields = ('animal', 'started_date', 'reproduction', 'finished_date')