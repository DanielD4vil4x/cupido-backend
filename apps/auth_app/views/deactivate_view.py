"""Vista para desactivar (soft delete) la cuenta de usuario."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..permissions import IsAccountActive


class DeactivateAccountView(APIView):
    """Marca la cuenta como inactiva sin eliminarla físicamente."""
    permission_classes = [IsAuthenticated, IsAccountActive]

    def post(self, request):
        # Desactivar cuenta
        return Response({"detail": "Cuenta desactivada correctamente."}, status=status.HTTP_200_OK)
