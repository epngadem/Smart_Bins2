from django.contrib import admin
from .models import Bin, DataCollection

# Enregistrement du modèle DataCollection dans l'admin
@admin.register(DataCollection)
class DataCollectionAdmin(admin.ModelAdmin):
    list_display = ('bin', 'timestamp', 'temperature', 'level', 'signal_strength')  # Colonnes affichées
    list_filter = ('bin', 'timestamp')  # Filtres disponibles
    search_fields = ('bin__bin_id', 'timestamp')  # Champs pour la recherche
    ordering = ('-timestamp',)  # Tri par défaut (décroissant par timestamp)

# Enregistrement du modèle Bin dans l'admin
@admin.register(Bin)
class BinAdmin(admin.ModelAdmin):
    list_display = ('bin_id', 'location', 'type', 'is_full', 'created_at', 'last_emptied_at')  # Colonnes affichées
    list_filter = ('type', 'is_full')  # Filtres disponibles
    search_fields = ('bin_id', 'location')  # Champs pour la recherche
    ordering = ('bin_id',)  # Tri par défaut (ascendant par bin_id)
    filter_horizontal = ('users',)  # Permet de gérer facilement les utilisateurs associés dans l'admin
