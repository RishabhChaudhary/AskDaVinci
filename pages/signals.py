from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Chats

@receiver(post_save, sender = User)
def create_chats(sender, instance, created, **kwargs):
    if created:
        Chats.objects.create(user=instance) 

# @receiver(post_save, sender = User)
# def save_chats(sender, instance, **kwargs):
#     # instance.save()
#     pass