# apps/profile_app/subapps/profile/serializers/get_profile_serializer.py

from rest_framework import serializers
from ..models import Perfil


class GetProfileSerializer(serializers.ModelSerializer):
    """
    Serializer para obtener datos del perfil.
    Incluye los campos especificados: usuario, programa_academico, ubicacion, hobbies, estatura, estado
    """

    class Meta:
        model = Perfil
        fields = [
            'usuario',
            'programa_academico',
            'ubicacion',
            'hobbies',
            'estatura',
            'estado'
        ]