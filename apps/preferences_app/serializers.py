# apps/preferences_app/serializers.py
from rest_framework import serializers
from .models import Preference, Filter

class PreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preference
        fields = '__all__'  # ← Usa todos los campos que SÍ existen
        # O lista solo los campos reales del modelo:
        # fields = ['id', 'rango_edad_min', 'rango_edad_max', 
        #           'rango_estatura_min', 'rango_estatura_max', 
        #           'ubicacion', 'genero_preferido', 'hobbies_preferidos']

class FilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filter
        fields = ['id', 'usuario', 'filter_types', 'filter_values']
        read_only_fields = ['id']