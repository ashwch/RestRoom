from django import forms
from django.forms import ModelForm

from app.models import ExtendedUser


class ExtendedUserForm(ModelForm):
    first_name = forms.CharField(required=False, max_length=100)
    last_name = forms.CharField(required=False, max_length=100)

    class Meta:
        model = ExtendedUser
        fields = ['email', 'first_name', 'last_name', 'password']
