from django import forms

from .models import Contact, CivilStatus


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = (
            'first_name',
            'last_name',
            'phone',
            'email',
            'birthday',
            'direction',
            'province',
            'civil_status'
        )
        widgets = {
            'civil_status': forms.Select(
                choices=CivilStatus,
                attrs={
                    'class': 'form-control',
                }
            ),
        }
