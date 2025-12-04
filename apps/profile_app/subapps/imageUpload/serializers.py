from rest_framework import serializers
from django.conf import settings
from .models import Imagen
from .services import ImageProcessor, ContentModerator


# Lógica: Validaciones de imágenes (tipo, contenido inapropiado) y compresión automática.
# El tamaño se maneja mediante compresión, no rechazando la imagen.

class ImagenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Imagen
        fields = '__all__'
        read_only_fields = ('usuario',)

    def validate_imagen(self, imagen):
        # Validación de tipo de contenido
        allowed_types = [
            'image/jpeg',
            'image/png',
            'image/webp',
        ]

        # Algunos FileStorage wrappers pueden no incluir content_type, así que validamos con fallback
        content_type = getattr(imagen, 'content_type', None)
        if content_type and content_type not in allowed_types:
            raise serializers.ValidationError("El archivo debe ser una imagen (jpeg, png, webp).")

        # Comprimir imagen si excede el tamaño máximo (400KB)
        # Lógica: En lugar de rechazar, comprimimos automáticamente para mejor UX
        imagen = ImageProcessor.process_image(imagen)
        
        # Moderar contenido con Sightengine (desnudez, violencia, armas, drogas)
        # Lógica: Si el servicio falla, aceptamos la imagen (fail-open)
        is_acceptable, message = ContentModerator.moderate_image(imagen)
        if not is_acceptable:
            raise serializers.ValidationError(message)

        return imagen
