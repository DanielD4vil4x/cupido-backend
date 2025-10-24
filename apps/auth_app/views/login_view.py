"""Vista para el inicio de sesión de usuarios."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers.login_serializer import LoginSerializer


class LoginView(APIView):
    """Autentica un usuario y devuelve los tokens JWT."""
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            # Lógica de autenticación y generación de tokens irá aquí
            return Response({"detail": "Inicio de sesión exitoso."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
