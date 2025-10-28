# apps/auth_app/views/user_get_view.py

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.auth_app.serializers.user_get_serializer import serialize_user_profile
from apps.auth_app.utils.profile import compute_account_state


class UserGetView(APIView):
    """
    Endpoint para obtener todos los campos del perfil del usuario autenticado.
    
    - GET: Devuelve el estado del perfil y todos los datos del usuario.
    - Requiere autenticación.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        estado = compute_account_state(user)
        
        # Mantener sincronizado con el campo persistido si difiere
        if getattr(user, "estadocuenta", None) != estado:
            user.estadocuenta = estado
            user.save(update_fields=["estadocuenta"])

        # Serializar todos los campos del usuario
        user_data = serialize_user_profile(user)
        
        payload = {
            "estado": estado,
            "should_complete_profile": estado == "incompleta",
            "user": user_data,
        }
        
        return Response(payload, status=status.HTTP_200_OK)

