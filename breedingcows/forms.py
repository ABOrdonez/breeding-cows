from django import forms

from .models import BreedingCows


class BreedingCowForm(forms.ModelForm):
    class Meta:
        model = BreedingCows
        fields = (
        	'address',
        	'province',
        	'contact',
        	'entry_date',
        	'description'
        )
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'contact': forms.Select(attrs={'class': 'form-control'}),
        }
