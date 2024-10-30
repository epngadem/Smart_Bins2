# serializers.py
from rest_framework import serializers
from .models import Bin, DataCollection

class BinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bin
        fields = ['bin_id', 'location', 'capacity', 'type', 'status', 'created_at', 'last_emptied_at', 'users']

class DataCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataCollection
        fields = ['bin', 'level', 'temperature', 'timestamp', 'signal_strength']



