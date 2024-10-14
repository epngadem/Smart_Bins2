from django.shortcuts import render
from .models import Bin

def bin_list(request):
    # Récupérer toutes les poubelles avec leurs données collectées
    bins = Bin.objects.prefetch_related('data_collections').all()
    return render(request, 'garbage/bin_list.html', {'bins': bins})
