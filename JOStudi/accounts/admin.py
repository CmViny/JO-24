from django.contrib import admin
from .models import Utilisateur

@admin.register(Utilisateur)
class UtilisateurAdmin(admin.ModelAdmin):
    readonly_fields = ('code_utilisateur',)
    list_display = ('user', 'is_admin', 'code_utilisateur')
