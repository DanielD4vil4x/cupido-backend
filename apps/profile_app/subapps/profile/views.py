from rest_framework import generics, permissions, status,viewsets
from rest_framework.response import Response
from apps.profile_app.subapps.profile.models import Perfil
from apps.profile_app.subapps.profile.serializer import *
from apps.profile_app.subapps.profile.utils import get_or_create_user_profile


class ProfileUpdateView(generics.RetrieveUpdateAPIView):
    """
    Permite al usuario autenticado obtener o actualizar su propio perfil.
    """
    serializer_class = PerfilSerializer
    permission_classes = [permissions.IsAuthenticated]  # permissions.IsAuthenticated para exigir token de autenticacion

    def get_object(self):
        # Crea el perfil si no existe
        return get_or_create_user_profile(self.request.user)

    def patch(self, request, *args, **kwargs):
        perfil = self.get_object()
        serializer = self.get_serializer(perfil, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        perfil = self.get_object()
        serializer = self.get_serializer(perfil)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class PerfilDetailView(generics.RetrieveAPIView):
    """
    Permite obtener información de un perfil específico por ID.
    Ideal para mostrar el perfil de otro usuario.
    """
    queryset = Perfil.objects.all()
    serializer_class = PerfilSerializer
    permission_classes = [permissions.AllowAny]  # puedes cambiar a IsAuthenticated si prefieres

    def get(self, request, *args, **kwargs):
        perfil = self.get_object()
        serializer = self.get_serializer(perfil)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PerfilAdminUpdateView(generics.RetrieveUpdateAPIView):
    """
    Permite a un administrador ver o actualizar un perfil específico por ID.
    """
    queryset = Perfil.objects.all()
    serializer_class = PerfilSerializer
    permission_classes = [permissions.AllowAny]  # permissions.IsAdminUser para exigir token de autenticacion de administrador

    def patch(self, request, *args, **kwargs):
        perfil = self.get_object()
        serializer = self.get_serializer(perfil, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProgramaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Programa.objects.all()
    serializer_class = ProgramaSerializer


class UbicacionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ubicacion.objects.all()
    serializer_class = UbicacionSerializer
