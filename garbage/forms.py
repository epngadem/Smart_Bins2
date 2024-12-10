from django import forms
from .models import Bin, DataCollection
from django.contrib.auth.models import User

class BinForm(forms.ModelForm):
    class Meta:
        model = Bin
        fields = ['bin_id', 'location', 'capacity', 'type', 'status', 'last_emptied_at']

class DataCollectionForm(forms.ModelForm):
    class Meta:
        model = DataCollection
        fields = ['bin', 'level', 'temperature', 'signal_strength']  # Exclure 'timestamp'

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirmer le mot de passe")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password != password_confirm:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")

        return cleaned_data
