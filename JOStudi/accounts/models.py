import uuid
from django.db import models
from django.contrib.auth.models import User
from django_cryptography.fields import encrypt # type: ignore

class Utilisateur(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='utilisateur')
    age = models.IntegerField(null=True, blank=True)
    telephone = models.CharField(max_length=20, null=True, blank=True)
    adresse = models.CharField(max_length=255, null=True, blank=True)
    date_inscription = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    old_cart = models.TextField(blank=True, null=True)
    code_utilisateur = models.CharField(max_length=64, blank=True, null=True)
    totp_secret = encrypt(models.CharField(max_length=32, blank=True, null=True))
    is_2fa_verified = models.BooleanField(default=False)
    is_2fa_enabled = models.BooleanField(default=False)


    def __str__(self):
        return self.user.username