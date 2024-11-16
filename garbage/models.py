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

    bin_id = models.CharField(max_length=10, unique=True)
    location = models.CharField(max_length=100)
    capacity = models.FloatField()  # Capacité maximale de la poubelle (en litres)
    type = models.CharField(max_length=50, choices=BIN_TYPES, default='Autre')
    status = models.CharField(max_length=50, blank=True, default='Empty')
    created_at = models.DateTimeField(auto_now_add=True)
    last_emptied_at = models.DateTimeField(null=True, blank=True)
    users = models.ManyToManyField(User, related_name='bins_managed', blank=True)
    is_full = models.BooleanField(default=False)

    def update_status(self):
        """Mise à jour du statut de la poubelle en fonction du dernier niveau de remplissage"""
        latest_data = self.data_collections.order_by('-timestamp').first()
        if latest_data:
            self.is_full = latest_data.level >= 100  # Définir la poubelle comme pleine si le niveau atteint 100%
            self.status = 'Full' if self.is_full else 'Not Full'
            self.save()

    def __str__(self):
        return f"Bin {self.bin_id} at {self.location}"


class DataCollection(models.Model):
    bin = models.ForeignKey(Bin, related_name='data_collections', on_delete=models.CASCADE)
    level = models.FloatField()  # Niveau de remplissage en pourcentage
    temperature = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    signal_strength = models.FloatField(blank=True, null=True)

    def save(self, *args, **kwargs):
        """Met à jour l'état de la poubelle lors de la collecte de nouvelles données"""
        super().save(*args, **kwargs)
        self.bin.update_status()  # Appel de la méthode update_status() de Bin pour ajuster son statut

    def __str__(self):
        return f"DataCollection for {self.bin.bin_id} at {self.timestamp}"




