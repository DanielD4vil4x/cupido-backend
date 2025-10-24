"""Vista para obtener información del usuario autenticado."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..permissions import IsAccountActive


class SessionInfoView(APIView):
    """Devuelve los datos del usuario autenticado."""
    permission_classes = [IsAuthenticated, IsAccountActive]

    def get(self, request):
        user = request.user
        data = {
            "id": user.id,
            "email": getattr(user, "email", None),
            "is_active": user.is_active,
        }
        return Response(data, status=status.HTTP_200_OK)
