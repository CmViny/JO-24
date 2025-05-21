import uuid
from django.db import models
from django.utils import timezone
from accounts.models import Utilisateur
from offers.models import Offre

import uuid
from io import BytesIO
from django.core.files.base import ContentFile
from django.db import models
import qrcode # type: ignore

class Transaction(models.Model):
    EN_ATTENTE = 'en_attente'
    REUSSIE = 'reussie'
    ECHOUEE = 'echouee'

    STATUT_CHOICES = [
        (EN_ATTENTE, 'En attente'),
        (REUSSIE, 'Réussie'),
        (ECHOUEE, 'Échouée'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    montant = models.DecimalField(max_digits=6, decimal_places=2)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default=EN_ATTENTE)
    date_transaction = models.DateTimeField(default=timezone.now)
    code_transaction = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return f"Transaction {self.id}"
    
    def generate_code_transaction(self, *args, **kwargs):
        if not self.code_transaction:
            self.code_transaction = uuid.uuid4().hex
            self.save(*args, **kwargs)

class Reservation(models.Model):
    EN_ATTENTE = 'en_attente'
    CONFIRMEE = 'confirmee'

    STATUT_CHOICES = [
        (EN_ATTENTE, 'En attente'),
        (CONFIRMEE, 'Confirmée'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    offre = models.ForeignKey(Offre, on_delete=models.CASCADE)
    date_reservation = models.DateTimeField(default=timezone.now)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default=EN_ATTENTE)
    transaction = models.ForeignKey(Transaction, null=True, blank=True, on_delete=models.SET_NULL)
    type_billet = models.CharField(max_length=20, choices=[('solo', 'Solo'), ('duo', 'Duo'), ('famille', 'Famille')], default='solo')


    def __str__(self):
        return f"Réservation {self.id}"


class QRCode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE)
    code = models.CharField(max_length=255, unique=True)
    date_generation = models.DateTimeField(default=timezone.now)
    image = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"QR {self.reservation}" 