"""
URL configuration for smart project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.contrib.auth.views import LogoutView, LoginView
from garbage.views import bin_detail_view
from django.conf import settings
from django.conf.urls.static import static

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', bin_detail_view, name='home'),  # Page d'accueil par défaut
    path('garbage/', include('garbage.urls')),  # Inclut les URLs de l'application garbage
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # API pour obtenir un token
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # API pour rafraîchir un token
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),  # Déconnexion
    path('login/', LoginView.as_view(template_name='garbage/login.html'), name='login'),  # Connexion
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)