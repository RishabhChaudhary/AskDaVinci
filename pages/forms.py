from django import forms
from django.contrib.auth.models import User
from .models import Chats

class ChatUpdate(forms.ModelForm):
    
    class Meta:
        model = Chats
        fields = ['question', 'answer']
