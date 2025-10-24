"""Vistas para recuperación de contraseña (solicitud y confirmación)."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers.password_reset_serializer import (
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)


class PasswordResetRequestView(APIView):
    """Solicita el restablecimiento de contraseña enviando un email con token."""
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            # Enviar email con token
            return Response({"detail": "Correo de recuperación enviado."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """Confirma el restablecimiento de contraseña con token."""
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            # Verificar token y actualizar contraseña
            return Response({"detail": "Contraseña restablecida correctamente."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
