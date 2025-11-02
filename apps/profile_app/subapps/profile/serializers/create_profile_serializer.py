# apps/profile_app/subapps/profile/serializers/create_profile_serializer.py

from rest_framework import serializers
from ..models import Perfil
from ..utils.create_profile_util import create_profile_for_user


class CreateProfileSerializer(serializers.Serializer):
    """
    Serializer para crear perfil automáticamente.
    No requiere campos de entrada, crea con valores por defecto.
    """

    def create(self, validated_data):
        user = self.context['request'].user
        return create_profile_for_user(user)