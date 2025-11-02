# apps/profile_app/subapps/profile/views/get_profile_view.py

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers.get_profile_serializer import GetProfileSerializer
from ..utils.get_profile_util import get_profile_data


class GetProfileView(APIView):
    """
    Endpoint para obtener datos del perfil del usuario autenticado.
    GET: Devuelve usuario, programa_academico, ubicacion, hobbies, estatura, estado
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        perfil_data = get_profile_data(request.user)
        if perfil_data:
            serializer = GetProfileSerializer(perfil_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {"error": "Perfil no encontrado."},
            status=status.HTTP_404_NOT_FOUND
        )