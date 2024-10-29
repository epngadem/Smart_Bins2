from django.shortcuts import render, redirect
from django.db.models import Avg
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from .models import Bin, DataCollection
from .forms import BinForm, DataCollectionForm
from .serializers import BinSerializer, DataCollectionSerializer

# Afficher la liste des poubelles avec alertes
def bin_list(request):
    bins = Bin.objects.all()
    
    for bin in bins:
        latest_data = bin.data_collections.latest('timestamp') if bin.data_collections.exists() else None
        
        if latest_data:
            # Détection des niveaux de remplissage
            if latest_data.level < 30:
                bin.alert_level = "green"
                bin.alert_message = "Poubelle moins de 30% pleine"
            elif 30 <= latest_data.level <= 70:
                bin.alert_level = "orange"
                bin.alert_message = "Poubelle entre 30% et 70% pleine"
            else:
                bin.alert_level = "red"
                bin.alert_message = "Poubelle plus de 70% pleine"
            
            # Détection des températures
            if latest_data.temperature > 25:
                bin.temperature_alert = "red"
                bin.temperature_message = f"Température élevée : {latest_data.temperature} °C"
            else:
                bin.temperature_alert = None
                bin.temperature_message = None
        else:
            bin.alert_level = None
            bin.alert_message = "Aucune donnée de collecte disponible"
            bin.temperature_alert = None
            bin.temperature_message = None
    
    return render(request, 'garbage/bin_list.html', {'bins': bins})

# Accueil
def home(request):
    return render(request, 'garbage/home.html')

# Ajouter une poubelle
def add_bin(request):
    if request.method == 'POST':
        form = BinForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('bin_list')
    else:
        form = BinForm()
    return render(request, 'garbage/add_bin.html', {'form': form})

# Ajouter des données à une poubelle
def add_data(request):
    if request.method == 'POST':
        form = DataCollectionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('bin_list')
    else:
        form = DataCollectionForm()
    return render(request, 'garbage/add_data.html', {'form': form})

# Vue pour afficher une seule poubelle avec ses données
def bin_detail(request, bin_id):
    bin = Bin.objects.get(pk=bin_id)
    data_collections = bin.data_collections.all()
    return render(request, 'garbage/bin_detail.html', {'bin': bin, 'data_collections': data_collections})

# Vue pour calculer et afficher la moyenne des températures
def moyenne_temperature(request):
    moyenne = DataCollection.objects.all().aggregate(Avg('temperature'))['temperature__avg']
    return render(request, 'garbage/moyenne_temperature.html', {'moyenne': moyenne})

class BinViewSet(viewsets.ModelViewSet):
    queryset = Bin.objects.all()
    serializer_class = BinSerializer

class DataCollectionViewSet(viewsets.ModelViewSet):
    queryset = DataCollection.objects.all()
    serializer_class = DataCollectionSerializer