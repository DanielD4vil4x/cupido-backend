from rest_framework import serializers
from .models import Imagen

class ImagenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Imagen
        fields = '__all__'
        read_only_fields = ('usuario',)
