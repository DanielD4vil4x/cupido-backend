# serializers/register_serializer.py
from rest_framework import serializers

class RegisterSerializer(serializers.Serializer):
    """Valida datos de registro de usuario."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    tyc = serializers.BooleanField()
