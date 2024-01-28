from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import ChatFiles

@receiver(post_save, sender = User)
def create_chat_file(sender, instance, created, **kwargs):
    if created:
        ChatFiles.objects.create(user=instance) 

@receiver(post_save, sender = User)
def save_chat_file(sender, instance, **kwargs):
    instance.chatfiles.save()