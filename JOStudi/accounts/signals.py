from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Utilisateur
import uuid

@receiver(post_save, sender=User)
def create_utilisateur(sender, instance, created, **kwargs):
    if created:
        Utilisateur.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_utilisateur(sender, instance, **kwargs):
    if hasattr(instance, 'utilisateur'):
        instance.utilisateur.save()

@receiver(post_save, sender=Utilisateur)
def generate_user_code(sender, instance, created, **kwargs):
    if created and not instance.code_utilisateur:
        instance.code_utilisateur = uuid.uuid4().hex
        instance.save()