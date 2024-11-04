# garbage/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import BinViewSet, DataCollectionViewSet, TemperatureDataAPIView

# Création du routeur DRF pour les API
router = DefaultRouter()
router.register(r'bins', BinViewSet)
router.register(r'data', DataCollectionViewSet)

# Définition des URLs
urlpatterns = [
    path('', views.bin_list, name='bin_list'),  # Page principale avec la liste des poubelles
    path('add/', views.add_bin, name='add_bin'),  # Ajouter une poubelle
    path('data/add/', views.add_data, name='add_data'),  # Ajouter des données
    path('home/', views.home, name='home'),  # Page d'accueil
    path('moyenne-temperature/', views.moyenne_temperature, name='moyenne_temperature'),  # Moyenne des températures
    path('api/', include(router.urls)),  # Inclusion des URLs du routeur API
    path('api/temperature/', TemperatureDataAPIView.as_view(), name='temperature_data_api'),
]
