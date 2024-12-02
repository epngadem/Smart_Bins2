# garbage/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from django.contrib.auth.views import LogoutView
from .views import BinViewSet, DataCollectionViewSet, TemperatureDataAPIView, BinDataView
from .views import fetch_latest_data
from django.contrib.auth.views import LoginView

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
    path('api/data/', views.collect_data, name='collect_data'),
    path('bins/', views.bin_list, name='bin_list'),
    path('bin/<int:bin_id>/', views.single_bin_view, name='single_bin'),
    path('bin/1/', views.bin_detail_view, name='bin_detail'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('api/bin/<str:bin_id>/', BinDataView.as_view(), name='bin_data_view'),
    path('api/bin/<str:bin_id>/latest/', fetch_latest_data),
    path('login/', LoginView.as_view(template_name='garbage/login.html'), name='login'),
    #path('bins/', views.user_bins_view, name='user_bins'),
    #path('login/', views.user_login, name='login'),
    #path('logout/', views.user_logout, name='logout'),
    #path('bins/', views.user_bins_view, name='user_bins'),
    #path('bin/<str:bin_id>/', views.bin_detail_view, name='bin_detail'),
]

    



