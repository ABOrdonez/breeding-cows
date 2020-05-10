from django import forms
from .models import Reproduction

class ReproductionForm(forms.ModelForm):
    class Meta:
        model = Reproduction
        fields = ('give_birth_date','reproduction_type', 'preparation_date', 'execution_date', 'revision_date', 'success_revision', 'separation_date')
