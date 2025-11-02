from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.perfil.serializers.perfil_serializer import PerfilSerializer
from apps.perfil.utils.perfil_utils import PerfilUtils

class PerfilView(APIView):
    """
    Vista para creación de perfiles
    """

    def post(self, request):
        serializer = PerfilSerializer(data=request.data)
        if serializer.is_valid():
            try:
                perfil = PerfilUtils.create_perfil(serializer.validated_data)
                return Response(
                    {"message": "Perfil creado exitosamente", "perfil_id": perfil.perfil_id},
                    status=status.HTTP_201_CREATED
                )
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": f"Error inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
