from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.auth_app.serializers.profile_update_serializer import ProfileUpdateSerializer
from apps.auth_app.utils.profile import compute_account_state, is_profile_complete


class ProfileUpdateView(APIView):
    """
    Gestiona el flujo de actualización de perfil.

    - GET: Devuelve el estado del perfil del usuario autenticado y datos básicos.
    - PATCH: Actualiza el perfil con nombres, apellidos, género, fecha de nacimiento y descripción.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        estado = compute_account_state(user)
        # Mantener sincronizado con el campo persistido si difiere
        if getattr(user, "estadocuenta", None) != estado:
            user.estadocuenta = estado
            user.save(update_fields=["estadocuenta"])

        payload = {
            "estado": estado,
            "should_complete_profile": estado == "incompleta",
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
        return Response(payload, status=status.HTTP_200_OK)

    def patch(self, request):
        user = request.user
        serializer = ProfileUpdateSerializer(instance=user, data=request.data, partial=True)
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


