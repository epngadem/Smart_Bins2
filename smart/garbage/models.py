from django.db import models
from django.contrib.auth.models import User

from django.db import models

class Bin(models.Model):
    BIN_TYPES = [
        ('Plastique', 'Plastique'),
        ('Papier', 'Papier'),
        ('Verre', 'Verre'),
        ('Métal', 'Métal'),
        ('Déchets organiques', 'Déchets organiques'),
        ('Autre', 'Autre'),
    ]

    bin_id = models.CharField(max_length=10, unique=True)
    location = models.CharField(max_length=100)
    capacity = models.FloatField()  # Capacité maximale de la poubelle (en litres)
    type = models.CharField(max_length=50, choices=BIN_TYPES, default='Autre')  # Choix prédéfinis pour le type de poubelle
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    last_emptied_at = models.DateTimeField(null=True, blank=True)
    users = models.ManyToManyField('auth.User', related_name='bins_managed', blank=True)

    def __str__(self):
        return f"Bin {self.bin_id} at {self.location}"


class DataCollection(models.Model):
    bin = models.ForeignKey(Bin, on_delete=models.CASCADE, related_name='data_collections')
    level = models.FloatField()
    temperature = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    signal_strength = models.FloatField()

    def __str__(self):
        return f"Data for {self.bin.bin_id} at {self.timestamp}"
