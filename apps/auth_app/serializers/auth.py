from rest_framework import serializers
from legacy_models.models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
    """
    Serializa los datos básicos del usuario para las respuestas JSON.
    """
    class Meta:
        model = Usuario
        fields = ["usuario_id", "nombres", "email"]


class LoginSerializer(serializers.Serializer):
    """
    Valida los campos de login.
    """
    email = serializers.EmailField()
    contrasena = serializers.CharField(write_only=True)
