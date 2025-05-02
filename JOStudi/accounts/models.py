import uuid
from django.db import models

class Utilisateur(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=100)
    email = models.EmailField(max_length=255 ,unique=True)
    mot_de_passe = models.CharField(max_length=255)
    date_inscription = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.nom