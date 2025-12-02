# notificacion_app/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import notificacion
from .serializers import NotificacionSerializer
from django.core.cache import cache

class NotificacionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para CRUD de notificaciones.
    - lista: solo notificaciones del usuario autenticado
    - retrieve: ver detalle (solo si es propietario)
    - partial_update / update / destroy: por defecto pueden hacerse (se pueden restringir)
    - mark_read: acción personalizada para marcar una notificación como leída
    """
    serializer_class = NotificacionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # solo devuelve las notificaciones del usuario autenticado
        user = self.request.user
        return notificacion.objects.filter(usuario_destino=user).order_by('-fecha_envio')


    @action(detail=True, methods=['post'], url_path='mark_read')
    def mark_read(self, request, pk=None):
        """
        Marca la notificación como 'leido' (solo si pertenece al usuario).
        Método: POST /api/notifications/{id}/mark_read/
        """
        # Obtener la instancia o 404 (consulta ya está restringida por get_queryset)
        try:
            instance = self.get_object()
        except Exception:
            return Response({"detail": "Notificación no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        # Verificar propietario (get_object con queryset limita, pero doble chequeo)
        if instance.usuario_destino != request.user:
            return Response({"detail": "No tienes permiso para modificar esta notificación."},
                            status=status.HTTP_403_FORBIDDEN)

        # Si ya está leída, devolvemos la instancia (idempotente)
        if instance.estado == notificacion.STATUS_READ:
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Actualizamos en una transacción
        with transaction.atomic():
            instance.estado = notificacion.STATUS_READ
            instance.save(update_fields=['estado'])

        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
    @action(detail=False, methods=['post'], url_path='chat_abierto')
    def chat_abierto(self, request):
        chat_id = request.data.get("chat_id")

        if not chat_id:
            return Response({"detail": "chat_id es requerido"}, status=400)

        cache_key = f"chat_abierto_usuario_{request.user.id}"
        cache.set(cache_key, chat_id, 60 * 30)  # 30 min

        return Response({"detail": "chat marcado como abierto"})

    @action(detail=False, methods=['post'], url_path='chat_cerrado')
    def chat_cerrado(self, request):
        cache_key = f"chat_abierto_usuario_{request.user.id}"
        cache.delete(cache_key)

        return Response({"detail": "chat cerrado"})
