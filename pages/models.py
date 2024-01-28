from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Chats(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE) 
    question = models.TextField()
    answer = models.TextField()

    def __str__(self) -> str:
        return f'{self.question} Question'

    