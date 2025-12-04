from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from .models import Imagen
from .serializers import ImagenSerializer
from django.conf import settings


class ImagenListCreateView(generics.ListCreateAPIView):
    """
    GET: Lista las imágenes del usuario autenticado.
    POST: Sube una nueva imagen (con compresión y moderación automática).
    """
    queryset = Imagen.objects.all()
    serializer_class = ImagenSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return self.queryset.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        # Lógica de negocio: limitar cantidad maxima de fotos por usuario
        max_photos = getattr(settings, 'PHOTO_MAX_FILES', 3)
        current_count = Imagen.objects.filter(usuario=self.request.user).count()
        if current_count >= max_photos:
            raise ValidationError({'detail': f"Has alcanzado el máximo de {max_photos} imágenes permitidas."})
        serializer.save(usuario=self.request.user)


class ImagenDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Obtiene detalle de una imagen específica.
    PUT/PATCH: Actualiza una imagen (ej: marcar como principal).
    DELETE: Elimina una imagen.
    """
    queryset = Imagen.objects.all()
    serializer_class = ImagenSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(usuario=self.request.user)


class ImagenStatusView(APIView):
    """
    GET: Verifica si el usuario cumple con el mínimo de fotos requeridas.
    
    Lógica de negocio: El usuario debe tener al menos 1 foto para poder
    avanzar del paso de carga de imágenes. Este endpoint permite al frontend
    validar antes de permitir el avance.
    
    Response:
        {
            "has_minimum": true/false,
            "current_count": N,
            "minimum_required": 1,
            "maximum_allowed": 3,
            "can_upload_more": true/false
        }
    """
    permission_classes = [IsAuthenticated]
    
    MINIMUM_PHOTOS = 1  # Mínimo requerido para avanzar

    def get(self, request):
        current_count = Imagen.objects.filter(usuario=request.user).count()
        max_photos = getattr(settings, 'PHOTO_MAX_FILES', 3)
        
        return Response({
            'has_minimum': current_count >= self.MINIMUM_PHOTOS,
            'current_count': current_count,
            'minimum_required': self.MINIMUM_PHOTOS,
            'maximum_allowed': max_photos,
            'can_upload_more': current_count < max_photos,
        })
