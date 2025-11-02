# apps/profile_app/subapps/profile/views/create_profile_view.py

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers.create_profile_serializer import CreateProfileSerializer


class CreateProfileView(APIView):
    """
    Endpoint para crear perfil automáticamente.
    POST: Crea perfil con valores por defecto para el usuario autenticado.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CreateProfileSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            perfil = serializer.save()
            return Response(
                {
                    "message": "Perfil creado exitosamente.",
                    "perfil_id": perfil.perfil_id
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)