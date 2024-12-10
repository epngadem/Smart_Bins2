from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import user_login, bin_list
from django.contrib.auth.views import LogoutView
from garbage.views import user_register
from . import views
from .views import (
    BinViewSet,
    DataCollectionViewSet,
    TemperatureDataAPIView,
    BinDataView,
    fetch_latest_data,
)

# Création du routeur DRF pour les API
router = DefaultRouter()
router.register(r'bins', BinViewSet)
router.register(r'data', DataCollectionViewSet)

# Définition des URLs
urlpatterns = [
    # Pages normales
    # path('', views.bin_list, name='bin_list'),  # Liste des poubelles
    path('add/', views.add_bin, name='add_bin'),  # Ajouter une poubelle
    path('data/add/', views.add_data, name='add_data'),  # Ajouter des données
    path('home/', views.home, name='home'),  # Page d'accueil
    path('moyenne-temperature/', views.moyenne_temperature, name='moyenne_temperature'),  # Moyenne des températures
    path('bin/<int:bin_id>/', views.single_bin_view, name='single_bin'),  # Vue d'une seule poubelle
    path('register/', views.user_register, name='register'),  # Ajout du chemin pour l'inscription
    path('login/', user_login, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('bins/', bin_list, name='bin_list'),
    path('user_bins/', views.user_bins, name='user_bins'), 
    path('register/', user_register, name='register'),

    # API
    path('api/', include(router.urls)),  # Inclusion des URLs du routeur API
    path('api/temperature/', TemperatureDataAPIView.as_view(), name='temperature_data_api'),
    path('api/data/', views.collect_data, name='collect_data'),
    path('api/bin/<str:bin_id>/', BinDataView.as_view(), name='bin_data_view'),
    path('api/bin/<str:bin_id>/latest/', fetch_latest_data, name='fetch_latest_data'),
]
