# apps/auth_app/serializers/session_serializer.py
from rest_framework import serializers
from apps.auth_app.serializers.usuario_serializer import UsuarioSerializer


class SessionSerializer(serializers.Serializer):
    """
    Serializa la información de la sesión activa del usuario autenticado.
    Incluye los datos básicos del usuario y un mensaje descriptivo.
    Preparado para ampliarse con roles, expiración, metadata, etc.
    """

    message = serializers.CharField(default="Sesión activa.")
    user = UsuarioSerializer()
    # Campos futuros potenciales:
    # roles = serializers.ListField(child=serializers.CharField(), default=[])
    # token_expires_in = serializers.IntegerField(required=False)
    # last_login = serializers.DateTimeField(required=False)
    # ip_address = serializers.CharField(required=False)
    # device_info = serializers.CharField(required=False)
