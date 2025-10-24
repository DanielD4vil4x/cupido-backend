"""Vista para el registro de nuevos usuarios."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers.register_serializer import RegisterSerializer


class RegisterView(APIView):
    """
    Registra un nuevo usuario y envía el código de verificación por correo.
    """
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            # Lógica de creación y envío de código irá aquí
            return Response({"detail": "Usuario registrado correctamente."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
