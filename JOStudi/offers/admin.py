from django.contrib import admin
from .models import Offre
from reservations.models import Reservation

class OffreAdmin(admin.ModelAdmin):
    list_display = ('titre', 'prix', 'nombre_ventes')

    def nombre_ventes(self, obj):
        return Reservation.objects.filter(offre=obj).count()
    nombre_ventes.short_description = "Nombre de ventes"

admin.site.register(Offre, OffreAdmin)