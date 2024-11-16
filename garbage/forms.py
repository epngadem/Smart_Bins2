from django import forms
from .models import Bin, DataCollection

class BinForm(forms.ModelForm):
    class Meta:
        model = Bin
        fields = ['bin_id', 'location', 'capacity', 'type', 'status', 'last_emptied_at']

class DataCollectionForm(forms.ModelForm):
    class Meta:
        model = DataCollection
        fields = ['bin', 'level', 'temperature', 'signal_strength']  # Exclure 'timestamp'
