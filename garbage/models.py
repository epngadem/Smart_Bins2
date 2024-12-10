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

    def __str__(self):
        return f"Poubelle {self.bin_id} - {self.location}"

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
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Rendre le champ optionnel

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.bin.update_status()

    class Meta:
        permissions = [
            ("can_view_bin_data", "Peut voir les données des poubelles"),
            ("can_edit_bin_data", "Peut modifier les données des poubelles"),
        ]

    def __str__(self):
        return f"DataCollection for {self.bin.bin_id} at {self.timestamp}"
