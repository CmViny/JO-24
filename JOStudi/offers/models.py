import uuid
from decimal import Decimal
from django.db import models
import os
import requests
from dotenv import load_dotenv

load_dotenv()

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
    image_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.titre

    def get_prix(self, type_billet):
        multiplicateurs = {
            self.SOLO: Decimal('1'),
            self.DUO: Decimal('1.5'),
            self.FAMILLE: Decimal('2'),
        }
        return self.prix * multiplicateurs.get(type_billet, Decimal('1'))

    def save(self, *args, **kwargs):
        if self.image and not self.image_url:
            self.image.seek(0)
            file_data = self.image.read()
            file_name = self.image.name.split("/")[-1]

            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_KEY')
            bucket = os.getenv('SUPABASE_BUCKET')

            upload_url = f"{supabase_url}/storage/v1/object/{bucket}/offres/{file_name}"
            headers = {
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": "application/octet-stream",
                "x-upsert": "true"
            }

            response = requests.put(upload_url, headers=headers, data=file_data)

            if response.status_code in [200, 201]:
                self.image_url = f"{supabase_url}/storage/v1/object/public/{bucket}/offres/{file_name}"
            else:
                raise Exception(f"Échec de l’upload vers Supabase : {response.text}")

        super().save(*args, **kwargs)