# apps/auth_app/views/user_update_view.py

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.auth_app.serializers.user_update_serializer import UserUpdateSerializer
from apps.auth_app.utils.profile import is_profile_complete


class UserUpdateView(APIView):
    """
    Gestiona el flujo de actualización de perfil.

    - PATCH: Actualiza el perfil con nombres, apellidos, género, fecha de nacimiento y descripción.
    """

    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        user = request.user
        serializer = UserUpdateSerializer(instance=user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Refrescar el usuario desde la BD
        user.refresh_from_db()

        # Si el perfil ahora cumple mínimos, actualizar estado a 'completa'
        if is_profile_complete(user) and user.estadocuenta != "completa":
            user.estadocuenta = "completa"
            user.save(update_fields=["estadocuenta"])

        response = {
            "message": "Perfil actualizado correctamente.",
            "estado": user.estadocuenta,
            "user": {
                "usuario_id": user.usuario_id,
                "nombres": user.nombres,
                "apellidos": user.apellidos,
                "email": user.email,
                "genero": user.genero.genero_id if user.genero else None,
                "genero_descripcion": user.genero.descripcion if user.genero else None,
                "fechanacimiento": user.fechanacimiento,
                "descripcion": user.descripcion,
            },
        }
        return Response(response, status=status.HTTP_200_OK)


