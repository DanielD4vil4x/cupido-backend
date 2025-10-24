import logging
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from apps.auth_app.serializers.login_serializer import LoginSerializer
from apps.auth_app.serializers.usuario_serializer import UsuarioSerializer
from apps.auth_app.utils.tokens import create_jwt_for_user
from apps.auth_app.models import UsuarioProxy

logger = logging.getLogger(__name__)


class LoginView(APIView):
    """
    Endpoint de inicio de sesión.
    - Valida credenciales con LoginSerializer.
    - Genera y devuelve tokens JWT.
    - Rechaza accesos de usuarios menores de edad o credenciales inválidas.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        logger.info("🧩 Intento de inicio de sesión recibido.")
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        logger.debug(f"Tipo de user recibido: {type(user)}")

        # Verificar estado de cuenta antes de continuar
        if getattr(user, "estadocuenta", None) == "Menor":
            logger.warning(f"🚫 Intento de login bloqueado para menor de edad: {user.email}")
            return Response(
                {"error": "El acceso no está permitido para menores de edad."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Crear instancia de UsuarioProxy para compatibilidad con SimpleJWT
        try:
            user_proxy = UsuarioProxy.objects.get(pk=user.usuario_id)
        except UsuarioProxy.DoesNotExist:
            logger.error(f"❌ UsuarioProxy no encontrado para ID {user.usuario_id}")
            return Response(
                {"error": "Error interno al autenticar el usuario."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        logger.info(f"✅ Usuario validado correctamente: {user.email} (ID {user.usuario_id})")

        # Generar tokens JWT
        try:
            tokens = create_jwt_for_user(user_proxy)
            logger.info(f"🎫 Tokens JWT generados para usuario {user.email}")
        except Exception as e:
            logger.error(f"🔥 Error al generar tokens JWT para {user.email}: {e}")
            return Response(
                {"error": "Error interno al generar el token de autenticación."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Actualizar último inicio de sesión (si aplica)
        if hasattr(user_proxy, "last_login"):
            user_proxy.last_login = timezone.now()
            user_proxy.save(update_fields=["last_login"])
            logger.debug(f"🕓 last_login actualizado para {user.email}")

        # Construir respuesta
        response_payload = {
            "user": UsuarioSerializer(user_proxy).data,
            "access": tokens["access"],
            "refresh": tokens["refresh"],
        }

        logger.info(f"✅ Login exitoso para {user.email}")
        return Response(response_payload, status=status.HTTP_200_OK)