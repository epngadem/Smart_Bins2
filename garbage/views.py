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
from .models import Bin
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.db import connection


@api_view(['GET'])
@permission_classes([AllowAny])
def fetch_latest_data(request, bin_id='B001'):  # Définir une valeur par défaut pour bin_id
    """
    Vue pour récupérer les dernières données collectées pour une poubelle spécifique.
    Si aucun ID n'est fourni, 'B001' est utilisé par défaut.
    """
    try:
        # Récupérer la poubelle par son ID (par défaut 'B001' si non fourni)
        bin_instance = Bin.objects.get(bin_id=bin_id)

        # Récupérer les dernières données collectées
        latest_data = bin_instance.data_collections.order_by('-timestamp').first()

        if latest_data:
            data = {
                'timestamp': latest_data.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'level': latest_data.level,
                'temperature': latest_data.temperature,
                'signal_strength': latest_data.signal_strength,
                'is_full': latest_data.level > 70,
            }
            return Response(data, status=200)
        else:
            return Response({'error': "Aucune donnée disponible pour cette poubelle."}, status=404)

    except Bin.DoesNotExist:
        return Response({'error': f"Poubelle avec l'ID {bin_id} introuvable."}, status=404)

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
    permission_classes = [AllowAny]  # Permet l'accès public à cette API

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
    try:
        # Charger la poubelle spécifique (B001)
        bin = Bin.objects.get(bin_id='B001')
        data_collections = bin.data_collections.all().order_by('-timestamp')

        # Préparer les données pour le dernier point collecté
        latest_data = data_collections.first() if data_collections.exists() else None
        is_full = latest_data.level > 70 if latest_data else False

        # Préparer les données pour le graphique
        timestamps = []
        levels = []
        temperatures = []

        for data in data_collections:
            timestamps.append(data.timestamp.strftime('%Y-%m-%d %H:%M:%S'))
            levels.append(data.level)
            temperatures.append(data.temperature)

        chart_data = {
            "timestamps": timestamps,
            "levels": levels,
            "temperatures": temperatures,
        }

        # Convertir les données en JSON pour les transmettre au template
        chart_data_json = json.dumps(chart_data, cls=DjangoJSONEncoder)

        return render(request, 'garbage/bin_detail.html', {
            'bin': bin,
            'latest_data': latest_data,
            'is_full': is_full,
            'chart_data': chart_data_json,
        })
    except Bin.DoesNotExist:
        return render(request, 'garbage/bin_detail.html', {'error': "Poubelle introuvable."})
def check_bin_status(bin):
    if bin.is_full:  
        print(f"Alerte simulée : La poubelle {bin.bin_id} est presque pleine.")


from django.urls import path
from .views import fetch_latest_data

   
class BinDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, bin_id):
        try:
            data = DataCollection.objects.filter(bin__bin_id=bin_id).order_by('-timestamp').first()
            if data:
                return Response({
                    "bin_id": bin_id,
                    "temperature": data.temperature,
                    "level": data.level,
                    "timestamp": data.timestamp,
                    "signal_strength": data.signal_strength,
                }, status=200)
            else:
                return Response({"message": "Aucune donnée disponible pour cette poubelle."}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def post(self, request, bin_id):
        try:
            # Vérifiez si la poubelle existe
            bin_instance = Bin.objects.get(bin_id=bin_id)

            # Sérialiser les données reçues
            serializer = DataCollectionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(bin=bin_instance)
                return Response({"message": "Données enregistrées avec succès"}, status=201)
            return Response(serializer.errors, status=400)
        except Bin.DoesNotExist:
            return Response({"error": f"Poubelle avec bin_id {bin_id} introuvable"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

def index(request):
    try:
        # Récupérer la poubelle B001
        bin_b001 = Bin.objects.get(bin_id="B001")

        # Récupérer les données collectées pour la poubelle B001
        data_collections = DataCollection.objects.filter(bin=bin_b001).order_by('timestamp')

        # Préparer les données pour le graphique
        data = {
            'timestamps': [dc.timestamp.strftime('%Y-%m-%d %H:%M:%S') for dc in data_collections],
            'levels': [dc.level for dc in data_collections],
            'temperatures': [dc.temperature for dc in data_collections],
        }

        return render(request, 'garbage/index.html', {'bin': bin_b001, 'data': data})

    except Bin.DoesNotExist:
        return render(request, 'garbage/index.html', {'error': "Poubelle B001 introuvable."})


@login_required
def user_bins_view(request):
    user = request.user.username  # Récupérer le nom d'utilisateur
    table_prefix = f"{user}_bin_view"
    data_table_prefix = f"{user}_datacollection_view"

    try:
        with connection.cursor() as cursor:
            # Récupérer les poubelles
            cursor.execute(f"SELECT * FROM {table_prefix};")
            bins = cursor.fetchall()

            # Récupérer les données collectées
            cursor.execute(f"SELECT * FROM {data_table_prefix};")
            data_collections = cursor.fetchall()

        return render(request, 'garbage/user_bins.html', {
            'bins': bins,
            'data_collections': data_collections,
        })
    except Exception as e:
        return render(request, 'garbage/user_bins.html', {
            'error': str(e),
        })