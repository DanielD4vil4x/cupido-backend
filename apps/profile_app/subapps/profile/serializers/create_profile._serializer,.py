from rest_framework import serializers
from apps.perfil.models import Perfil

class PerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        fields = '__all__'

    def validate_estatura(self, value):
        if value is not None and (value < 0 or value > 3):
            raise serializers.ValidationError("La estatura debe estar entre 0 y 3 metros.")
        return value

    def validate(self, data):
        if not data.get('usuario'):
            raise serializers.ValidationError({"usuario": "El usuario es obligatorio."})
        return data
