import time
import requests

# URLs pour obtenir et rafraîchir les jetons et pour l'API des données
token_url = "http://127.0.0.1:8000/api/token/"
refresh_url = "http://127.0.0.1:8000/api/token/refresh/"
data_url = "http://127.0.0.1:8000/garbage/api/data/"

# Informations d'identification
credentials = {
    "username": "ornella",  # Remplacez par votre nom d'utilisateur
    "password": "1234"      # Remplacez par votre mot de passe
}

# Obtenir le jeton d'accès et le jeton de rafraîchissement
def obtenir_jetons():
    response = requests.post(token_url, json=credentials)
    if response.status_code == 200:
        tokens = response.json()
        return tokens["access"], tokens["refresh"]
    else:
        print("Erreur lors de l'obtention du jeton :", response.status_code, response.text)
        exit()

# Rafraîchir le jeton d'accès
def rafraichir_jeton(refresh_token):
    headers = {"Content-Type": "application/json"}
    response = requests.post(refresh_url, json={"refresh": refresh_token}, headers=headers)
    if response.status_code == 200:
        return response.json()["access"]
    else:
        print("Erreur lors du rafraîchissement du jeton :", response.status_code, response.text)
        exit()

# Initialiser les jetons
access_token, refresh_token = obtenir_jetons()

# Envoi des données avec gestion du jeton expiré
def envoyer_donnees(temperature, niveau_remplissage):
    global access_token
    data = {
        'temperature': temperature,
        'level': niveau_remplissage,
        'bin': 1  # Identifiant de la poubelle
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(data_url, json=data, headers=headers)
    if response.status_code == 201:
        print("Données envoyées avec succès :", response.json())
    elif response.status_code == 401:  # Cas où le jeton a expiré
        print("Jeton expiré, tentative de rafraîchissement...")
        access_token = rafraichir_jeton(refresh_token)
        headers["Authorization"] = f"Bearer {access_token}"
        response = requests.post(data_url, json=data, headers=headers)
        if response.status_code == 201:
            print("Données envoyées avec succès après rafraîchissement du jeton :", response.json())
        else:
            print("Erreur lors de l'envoi des données après rafraîchissement du jeton :", response.status_code, response.text)
    else:
        print("Erreur lors de l'envoi des données :", response.status_code, response.text)

# Boucle infinie pour envoyer les données périodiquement
while True:
    # Données du capteur (exemple de valeurs)
    temperature = 22.5  # Remplacez par la température mesurée
    niveau_remplissage = 45.0  # Remplacez par le niveau de remplissage mesuré
    
    envoyer_donnees(temperature, niveau_remplissage)
    
    # Pause de 2 secondes avant le prochain envoi
    time.sleep(2)
