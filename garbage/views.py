from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.decorators import api_view
from django.db.models import Avg
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from .models import Bin, DataCollection
from .forms import BinForm, DataCollectionForm
from .serializers import BinSerializer, DataCollectionSerializer, DataCollectionBoxSerializer
from rest_framework.permissions import IsAuthenticated
from .utils import send_alert_email
from .models import Bin
from django.utils import timezone
from django.contrib.auth.decorators import login_required


def bin_list(request):
    bins = Bin.objects.all()
    
    for bin in bins:
        # Récupérer les dernières données de collecte pour chaque poubelle
        latest_data = bin.data_collections.latest('timestamp') if bin.data_collections.exists() else None
        bin.latest_data = latest_data  # Ajouter les dernières données de collecte à chaque instance de bin
        
        # Définir les niveaux d'alerte pour chaque poubelle en fonction des données de remplissage et de température
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


class TemperatureDataAPIView(APIView):
    def post(self, request):
        # Sérialisation des données reçues
        serializer = DataCollectionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Sauvegarde des données dans la base de données
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        # Récupère toutes les collectes de données avec leurs températures, niveaux, et IDs de poubelle
        data = DataCollection.objects.values('bin__id', 'temperature', 'level', 'timestamp')
        return Response(data, status=status.HTTP_200_OK)

#def get(self, request):
        # Sérialisation des données reçues
        
        #moyenne = DataCollection.objects.all().aggregate(Avg('temperature'))['temperature__avg']
        #serializer = DataCollectionSerializer(data=moyenne)
        #return Response(moyenne, status=status.HTTP_200_OK)

 #def get(self, request):
        # Récupère toutes les collectes de données avec leurs températures, niveaux et IDs de poubelle
          #data_collections = bin.data_collections.values('temperature', 'level', 'timestamp')
         #return Response(data_collections, status=status.HTTP_200_OK)
       
        r #eturn Response(data, status=status.HTTP_200_OK)


        # Exemple d'utilisation dans views.py


def check_bin_status(bin):
    if bin.fill_level > 70:  # Condition d'alerte
        subject = f"Alerte : La poubelle {bin.id} est presque pleine"
        message = f"La poubelle {bin.id} est remplie à {bin.fill_level}%."
        send_alert_email(subject, message, ['destinataire@example.com'])

# @api_view(['POST'])
permission_classes = [IsAuthenticated]
def collect_data(request):
    serializer = DataCollectionBoxSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def single_bin_view(request, bin_id):
    bin = get_object_or_404(Bin, id=bin_id)
    latest_data = bin.data_collections.latest('timestamp') if bin.data_collections.exists() else None
    
    return render(request, 'garbage/single_bin.html', {'bin': bin, 'latest_data': latest_data})


@login_required
def bin_detail_view(request):
    # On récupère la poubelle avec l'identifiant 1
    bin = Bin.objects.get(bin_id='1')  
    data_collections = bin.data_collections.all().order_by('-timestamp')
    
    # Vérifie le statut de remplissage
    if data_collections.exists():
        latest_data = data_collections.first()
        bin.is_full = latest_data.level > 70  # Met à jour le statut
        bin.save()
        if bin.is_full:
            check_bin_status(bin)  # Appelle la fonction pour envoyer un email d'alerte

    return render(request, 'garbage/bin_detail.html', {
        'bin': bin,
        'data_collections': data_collections,
    })

def check_bin_status(bin):
    if bin.is_full:  
        subject = f"Alerte : La poubelle {bin.bin_id} est presque pleine"
        message = f"La poubelle {bin.bin_id} est remplie à {bin.capacity}%."
        send_alert_email(subject, message, ['komornella63@gmail.com'])