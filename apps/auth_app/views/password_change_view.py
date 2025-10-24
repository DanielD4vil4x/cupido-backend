"""Vista para cambio de contraseña estando autenticado."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..permissions import IsAccountActive
from ..serializers.password_change_serializer import PasswordChangeSerializer


class PasswordChangeView(APIView):
    """Permite al usuario cambiar su contraseña."""
    permission_classes = [IsAuthenticated, IsAccountActive]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            # Cambiar contraseña en base de datos
            return Response({"detail": "Contraseña cambiada exitosamente."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
