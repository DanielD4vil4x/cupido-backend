# notificacion_app/serializers.py
from rest_framework import serializers
from .models import notificacion

class NotificacionSerializer(serializers.ModelSerializer):
    usuario_destino = serializers.StringRelatedField()  # muestra username en vez de id

    class Meta:
        model = notificacion
        fields = ('id', 'tipo', 'mensaje', 'fecha_envio', 'estado', 'usuario_destino')
        read_only_fields = ('id', 'fecha_envio')
