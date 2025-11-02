from rest_framework import serializers
from apps.profile_app.subapps.profile.models import Perfil

class PerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        fields = "__all__"
        read_only_fields = ['perfil_id', 'usuario', 'fecharegistro']
