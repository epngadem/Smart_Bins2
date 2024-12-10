import psycopg2
from psycopg2 import OperationalError
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User

class PostgresAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Validation et nettoyage des données
            if not username or not password:
                print("Identifiant ou mot de passe manquant.")
                return None

            username = username.strip()
            password = password.strip()

            # Connexion à PostgreSQL pour valider les identifiants
            conn = psycopg2.connect(
                dbname='smartbin',
                user='postgres',  # Nom d'utilisateur PostgreSQL
                password='1234',  # Mot de passe PostgreSQL
                host='localhost',
                port='5432',
                options="-c client_encoding=UTF8"
            )
            conn.close()  # Connexion réussie, les identifiants sont valides

            # Vérifier si l'utilisateur existe dans Django
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_unusable_password()  # Le mot de passe ne sera pas stocké dans Django
                user.save()

            return user

        except OperationalError as e:
            # Erreurs de connexion à PostgreSQL
            print(f"Erreur PostgreSQL : {e}")
            return None

        except UnicodeDecodeError as e:
            # Erreurs d'encodage
            print(f"Erreur de décodage des identifiants : {e}")
            return None

        except Exception as e:
            # Capturer toute autre erreur
            print(f"Erreur inattendue : {e}")
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
