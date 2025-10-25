# apps/auth_app/views/verify_view.py
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from legacy_models.models import Usuario
from apps.auth_app.serializers.verify_serializer import VerifyEmailSerializer
# UsuarioProxy eliminado, ahora usamos Usuario directamente
from apps.auth_app.utils.redis_client import delete_key
from apps.auth_app.utils import codes

from rest_framework_simplejwt.tokens import RefreshToken


class VerifyEmailView(APIView):
    """
    Paso 2 del registro:
      - Valida email y código recibido
      - Recupera los datos temporales desde Redis
      - Crea el usuario definitivo en la base de datos
      - Devuelve mensaje de éxito (o tokens JWT opcionales)
    """

    throttle_scope = "verify_email"

    @transaction.atomic
    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        # Obtener los datos que fueron guardados temporalmente en Redis
        registration_payload = serializer.get_registration_payload()

        try:
            # Crear usuario en la base de datos con datos reales del registro
            user = Usuario.objects.create(
                nombres=registration_payload.get("nombres"),
                apellidos=registration_payload.get("apellidos"),
                email=email,
                password=registration_payload.get("password"),  # ya hasheada
                apodo=registration_payload.get("apodo", ""),
                numerotelefono=registration_payload.get("numerotelefono"),
                tyc=registration_payload.get("tyc", True),
                estadocuenta=registration_payload.get("estadocuenta", "Activa"),
                fecharegistro=registration_payload.get("fecharegistro"),
                fechanacimiento=registration_payload.get("fechanacimiento"),
                genero_id=registration_payload.get("genero_id"),
                programa_id=registration_payload.get("programa_id"),
                semestreubicacion_id=registration_payload.get("semestreubicacion_id"),
            )
        except Exception as e:
            return Response(
                {"error": f"No se pudo crear el usuario: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Eliminar datos temporales del registro y el código
        delete_key(f"register:{email}")
        codes.invalidate_code(email)

        # Generar tokens JWT (opcional)
        try:
            refresh = RefreshToken.for_user(user)
            tokens = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        except Exception as e:
            tokens = None

        return Response(
            {
                "message": "Cuenta verificada y creada exitosamente.",
                "user": {
                    "usuario_id": user.usuario_id,
                    "nombres": user.nombres,
                    "email": user.email,
                    "estadocuenta": user.estadocuenta,
                },
                **({"tokens": tokens} if tokens else {}),
            },
            status=status.HTTP_201_CREATED,
        )
