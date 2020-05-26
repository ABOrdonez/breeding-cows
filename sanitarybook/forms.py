from django import forms
from .models import Sanitary


class SanitaryForm(forms.ModelForm):
    class Meta:
        model = Sanitary
        fields = ('name', 'antiparasitic', 'copper', 'clostridiosis', 'animal_type', 'description')
