"""Vistas para verificación de correo electrónico y reenvío de código."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers.verify_serializer import VerifyEmailSerializer


class VerifyEmailView(APIView):
    """Valida el código de verificación de correo."""
    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        if serializer.is_valid():
            # Lógica de verificación del código irá aquí
            return Response({"detail": "Correo verificado correctamente."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendVerificationCodeView(APIView):
    """Reenvía el código de verificación."""
    def post(self, request):
        # Lógica para reenviar código irá aquí
        return Response({"detail": "Código reenviado correctamente."}, status=status.HTTP_200_OK)
