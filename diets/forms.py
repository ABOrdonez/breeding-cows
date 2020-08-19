from django import forms

from .models import Diet


class DietForm(forms.ModelForm):
    class Meta:
        model = Diet
        fields = (
            'name',
            'protein',
            'energies',
            'description',
            'animal_type'
        )

        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }
