# Django - Imports standard
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Avg
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

# Django REST Framework (DRF)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets

# Modèles, formulaires et sérialiseurs de l'application
from .models import Bin, DataCollection
from .forms import BinForm, DataCollectionForm, UserRegistrationForm
from .serializers import (
    BinSerializer,
    DataCollectionSerializer,
    DataCollectionBoxSerializer,
)

# Autres
from django.core.serializers.json import DjangoJSONEncoder
from .decorators import handle_db_permission_error
import json
from django.db import connection



from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages

def user_register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # Vérifiez si les mots de passe correspondent
        if password != confirm_password:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return redirect('register')

        # Vérifiez si l'utilisateur existe déjà
        if User.objects.filter(username=username).exists():
            messages.error(request, "Le nom d'utilisateur existe déjà.")
            return redirect('register')

        # Créez l'utilisateur
        user = User.objects.create_user(username=username, password=password)
        user.save()
        messages.success(request, "Votre compte a été créé avec succès. Vous pouvez maintenant vous connecter.")
        return redirect('login')

    return render(request, 'garbage/register.html')

@api_view(['GET'])
@permission_classes([AllowAny])
def fetch_latest_data(request, bin_id='B001'):  # Définir une valeur par défaut pour bin_id
    """
    Vue pour récupérer les dernières données collectées pour une poubelle spécifique.
    Si aucun ID n'est fourni, 'B001' est utilisé par défaut.
    """
    try:
        # Récupérer la poubelle par son ID (par défaut 'B001' si non fourni)
        bin_instance = Bin.objects.get(bin_id=bin_id, users=request.user)  # Corrigé l'indentation ici

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

@login_required
def bin_list(request):
    # Récupérer les poubelles associées à l'utilisateur connecté
    bins = Bin.objects.filter(users=request.user)

    # Parcourir les poubelles pour ajouter les dernières données et alertes
    for bin in bins:
        latest_data = bin.data_collections.latest('timestamp') if bin.data_collections.exists() else None
        bin.latest_data = latest_data

        if latest_data:
            # Alertes pour le niveau de remplissage
            if latest_data.level < 30:
                bin.alert_level = "green"
                bin.alert_message = "Poubelle moins de 30% pleine"
            elif 30 <= latest_data.level <= 70:
                bin.alert_level = "orange"
                bin.alert_message = "Poubelle entre 30% et 70% pleine"
            else:
                bin.alert_level = "red"
                bin.alert_message = "Poubelle plus de 70% pleine"

            # Alertes pour la température
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

@login_required
@handle_db_permission_error
def add_bin(request):
    if request.method == 'POST':
        form = BinForm(request.POST)
        if form.is_valid():
            bin = form.save(commit=False)
            bin.save()
            bin.users.add(request.user)  # Associe l'utilisateur connecté
            return redirect('bin_list')
    else:
        form = BinForm()
    return render(request, 'garbage/add_bin.html', {'form': form})

# Ajouter des données à une poubelle
@login_required
@handle_db_permission_error
def add_data(request):
    if request.method == 'POST':
        form = DataCollectionForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.user = request.user  # Associe l'utilisateur connecté
            data.save()
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
@handle_db_permission_error
def bin_detail_view(request, bin_id='B001'):
    try:
        # Charger la poubelle spécifique (par défaut 'B001')
        bin = Bin.objects.get(bin_id=bin_id, users=request.user)  # Vérifie que l'utilisateur est associé à la poubelle
        data_collections = bin.data_collections.all().order_by('-timestamp')[:20]

        # Préparer les données pour le dernier point collecté
        latest_data = data_collections.first() if data_collections.exists() else None
        is_full = latest_data.level > 70 if latest_data else False

        # Déterminer la classe Bootstrap pour l'alerte
        if latest_data:
            if latest_data.level > 80:
                alert_class = 'danger'
            elif latest_data.level > 50:
                alert_class = 'warning'
            else:
                alert_class = 'success'
        else:
            alert_class = 'secondary'  # Cas où aucune donnée n'est disponible

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
            'alert_class': alert_class,
        })
    except Bin.DoesNotExist:
        # Retourne une page 404 ou un message d'erreur si la poubelle n'existe pas ou si l'utilisateur n'y a pas accès
        return render(request, 'garbage/bin_detail.html', {'error': "Poubelle introuvable ou accès non autorisé."})


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

from django.contrib.auth import login, logout

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authentification de l'utilisateur
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Connecter l'utilisateur
            login(request, user)
            messages.success(request, "Connexion réussie !")
            return redirect('user_bins')  # Redirige vers la liste des poubelles
        else:
            # Afficher un message d'erreur si l'authentification échoue
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
            return render(request, 'garbage/login.html')
    return render(request, 'garbage/login.html')
def user_logout(request):
    logout(request)
    messages.info(request, "Déconnexion réussie.")
    return redirect('login')  # Redirige vers la page de connexion après déconnexion



@login_required
def bin_list(request):
    # Récupérer les poubelles gérées par l'utilisateur connecté
    bins = Bin.objects.filter(users=request.user)
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





@login_required
def user_bins(request):
    bins = Bin.objects.filter(users=request.user)
    data_collections = DataCollection.objects.filter(bin__in=bins).values(
        'timestamp', 'level', 'temperature'
    )
    data_collections_json = json.dumps(list(data_collections), cls=DjangoJSONEncoder)
    return render(request, 'garbage/user_bins.html', {
        'bins': bins,
        'data_collections': data_collections_json,
    })