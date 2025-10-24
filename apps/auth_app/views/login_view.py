# apps/auth_app/views/login_view.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.auth_app.serializers.login_serializer import LoginSerializer
from ..serializers.usuario_serializer import UsuarioSerializer
from apps.auth_app.utils.tokens import create_jwt_for_user
import logging

logger = logging.getLogger(__name__)


class LoginView(APIView):
    """
    Endpoint de inicio de sesión.
    - Valida credenciales usando LoginSerializer.
    - Genera y devuelve tokens JWT.
    - Bloquea acceso si el usuario es menor de edad o las credenciales son inválidas.
    """

    def post(self, request):
        logger.info("🧩 Intento de inicio de sesión recibido.")

        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        logger.info(f"✅ Usuario validado correctamente: {user.email} (ID {user.usuario_id})")

        try:
            tokens = create_jwt_for_user(user)
        except Exception as e:
            logger.error(f"❌ Error al generar tokens JWT para {user.email}: {e}")
            return Response(
                {"error": "Error interno al generar el token."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        response_payload = {
            "user": UsuarioSerializer(user).data,
            "access": tokens["access"],
            "refresh": tokens["refresh"],
        }

        logger.info(f"🎫 Login exitoso para {user.email}")
        return Response(response_payload, status=status.HTTP_200_OK)


