from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import ChatFiles

class UserSignUp(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserUpdate(forms.ModelForm):
    
    class Meta:
        model = ChatFiles
        fields = ['file']