from django import forms

from .models import BreedingCows


class BreedingCowForm(forms.ModelForm):
    class Meta:
        model = BreedingCows
        fields = ('location',)
