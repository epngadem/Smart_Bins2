from functools import wraps
from django.shortcuts import render
from psycopg2.errors import InsufficientPrivilege  # Importer l'erreur spécifique de permission

def handle_db_permission_error(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            # Exécution de la vue normale
            return view_func(request, *args, **kwargs)
        except InsufficientPrivilege as e:
            # Vérification de l'erreur spécifique de permission
            return render(request, 'error_page.html', {
                'message': "Vous n'avez pas les droits nécessaires pour accéder à cette ressource."
            })
        except Exception as e:
            # Autres erreurs de base de données
            return render(request, 'error_page.html', {
                'message': "Une erreur interne est survenue. Veuillez réessayer plus tard."
            })
    return _wrapped_view
