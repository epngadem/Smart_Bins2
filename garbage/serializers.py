# serializers.py
from rest_framework import serializers
from .models import Bin, DataCollection

class BinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bin
        fields = ['bin_id', 'location', 'capacity', 'type', 'status', 'created_at', 'last_emptied_at', 'users']

class DataCollectionSerializer(serializers.ModelSerializer):
    bin = serializers.SlugRelatedField(
        queryset=Bin.objects.all(),
        slug_field='bin_id'  # Utilise `bin_id` au lieu de la clé primaire
    )

    class Meta:
        model = DataCollection
        fields = ['bin', 'level', 'temperature', 'timestamp', 'signal_strength']
class DataCollectionBoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataCollection
        fields = ['bin', 'level', 'temperature', 'timestamp']



