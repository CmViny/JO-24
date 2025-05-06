from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Utilisateur

@receiver(post_save, sender=User)
def create_utilisateur(sender, instance, created, **kwargs):
    if created:
        Utilisateur.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_utilisateur(sender, instance, **kwargs):
    if hasattr(instance, 'utilisateur'):
        instance.utilisateur.save()
