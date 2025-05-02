import uuid
from django.db import models

class Offre(models.Model):
    SOLO = 'solo'
    DUO = 'duo'
    FAMILLE = 'famille'

    TYPE_CHOICES = [
        (SOLO, 'Solo'),
        (DUO, 'Duo'),
        (FAMILLE, 'Famille'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    titre = models.CharField(max_length=100, blank=False)
    description = models.TextField(blank=True, max_length=500)
    prix = models.DecimalField(max_digits=6, decimal_places=2)
    type_billet = models.CharField(max_length=20, choices=TYPE_CHOICES)
    date_disponible = models.DateField()
    image = models.ImageField(upload_to='uploads/offres/', null=True, blank=True)

    def __str__(self):
        return self.titre
    
    def get_prix(self, type_billet):
        # Dictionnaire des multiplicateurs pour chaque type de billet
        multiplicateurs = {
            self.SOLO: 1,
            self.DUO: 1.5,
            self.FAMILLE: 2,
        }

        # Retourner le prix en fonction du type de billet, ou le prix de base si type inconnu
        return self.prix * multiplicateurs.get(type_billet, 1)