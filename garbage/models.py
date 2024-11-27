from django.db import models
from django.contrib.auth.models import User

class Bin(models.Model):
    BIN_TYPES = [
        ('Plastique', 'Plastique'),
        ('Papier', 'Papier'),
        ('Verre', 'Verre'),
        ('Métal', 'Métal'),
        ('Déchets organiques', 'Déchets organiques'),
        ('Autre', 'Autre'),
    ]

    bin_id = models.CharField(max_length=10, unique=True)  # Identifiant unique
    location = models.CharField(max_length=100)  # Emplacement
    capacity = models.FloatField()  # Capacité maximale (en litres)
    type = models.CharField(max_length=50, choices=BIN_TYPES, default='Autre')  # Type de déchets
    status = models.CharField(max_length=50, blank=True, default='Empty')  # Statut (e.g., Pleine/Vide)
    created_at = models.DateTimeField(auto_now_add=True)  # Date de création
    last_emptied_at = models.DateTimeField(null=True, blank=True)  # Dernière vidange
    users = models.ManyToManyField(User, related_name='bins_managed', blank=True)  # Utilisateurs associés
    is_full = models.BooleanField(default=False)  # Indique si la poubelle est pleine

    # Méthode pour afficher une représentation lisible de la poubelle
    def __str__(self):
        return f"Poubelle {self.bin_id} - {self.location}"

    # Méthode pour vérifier si la poubelle est pleine et mettre à jour le statut
    def update_status(self):
        """Met à jour le statut de la poubelle en fonction de son dernier niveau."""
        latest_data = self.data_collections.order_by('-timestamp').first()
        if latest_data and latest_data.level >= 70:
            self.is_full = True
            self.status = "Pleine"
        else:
            self.is_full = False
            self.status = "Vide"
        self.save()

    class Meta:
        ordering = ['bin_id']  # Tri par identifiant


class DataCollection(models.Model):
    bin = models.ForeignKey(Bin, related_name='data_collections', on_delete=models.CASCADE)
    level = models.FloatField()  # Niveau de remplissage en pourcentage
    temperature = models.FloatField(null=True, blank=True)  # Température
    timestamp = models.DateTimeField(auto_now_add=True)  # Timestamp
    signal_strength = models.FloatField(blank=True, null=True)  # Force du signal (optionnel)

    def save(self, *args, **kwargs):
        """Met à jour l'état de la poubelle lors de la collecte de nouvelles données."""
        super().save(*args, **kwargs)
        self.bin.update_status()  # Appelle la méthode pour ajuster le statut de la poubelle

    def __str__(self):
        return f"DataCollection for {self.bin.bin_id} at {self.timestamp}"


