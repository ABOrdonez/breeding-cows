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
            'description': forms.Textarea(attrs={'class': 'form-control', 'required':'True'}),
            'contact': forms.Select(attrs={'class': 'form-control', 'required':'True'}),
        }
