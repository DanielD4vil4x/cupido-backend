# apps/auth_app/views/user_get_view.py

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.auth_app.utils.user_get import get_user_profile_data


class UserGetView(APIView):
    """
    Endpoint para obtener todos los campos del perfil del usuario autenticado.
    
    - GET: Devuelve el estado del perfil y todos los datos del usuario.
    - Requiere autenticación.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        payload = get_user_profile_data(user)
        return Response(payload, status=status.HTTP_200_OK)

