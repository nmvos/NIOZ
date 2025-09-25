from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

# Custom user registration form
class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    username = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'password1', 'password2']