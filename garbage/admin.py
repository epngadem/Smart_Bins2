from django.contrib import admin
from .models import Bin, DataCollection

# Enregistrement de DataCollection dans l'admin
@admin.register(DataCollection)
class DataCollectionAdmin(admin.ModelAdmin):
    list_display = ('bin', 'timestamp', 'temperature', 'level', 'signal_strength')
    list_filter = ('bin', 'timestamp')
    search_fields = ('bin__bin_id', 'timestamp')

# Enregistrement de Bin dans l'admin
@admin.register(Bin)
class BinAdmin(admin.ModelAdmin):
    list_display = ('bin_id', 'location', 'type', 'is_full', 'created_at', 'last_emptied_at')
    list_filter = ('type', 'is_full')
    search_fields = ('bin_id', 'location')



   
