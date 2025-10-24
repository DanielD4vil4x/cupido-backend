"""Vistas para cierre de sesión (simple o global)."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..permissions import IsAccountActive


class LogoutView(APIView):
    """Cierra la sesión actual (invalida el token)."""
    permission_classes = [IsAuthenticated, IsAccountActive]

    def post(self, request):
        # Lógica de invalidación del refresh token actual irá aquí
        return Response({"detail": "Sesión cerrada correctamente."}, status=status.HTTP_200_OK)


class LogoutAllView(APIView):
    """Cierra todas las sesiones activas del usuario."""
    permission_classes = [IsAuthenticated, IsAccountActive]

    def post(self, request):
        # Lógica para invalidar todos los tokens de este usuario irá aquí
        return Response({"detail": "Todas las sesiones cerradas correctamente."}, status=status.HTTP_200_OK)
