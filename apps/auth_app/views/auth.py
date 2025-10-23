import redis
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from legacy_models.models import Usuario
from apps.auth_app.serializers.auth import LoginSerializer, UsuarioSerializer
from apps.auth_app.models import UsuarioProxy

r = redis.StrictRedis.from_url(settings.REDIS_URL, decode_responses=True)

class RegisterView(APIView):
    """
    Paso 2 del registro:
    - Valida el código recibido
    - Crea el usuario en la base de datos
    - Devuelve mensaje de éxito
    """

    def post(self, request):
        email = request.data.get("email")
        codigo = request.data.get("codigo")

        # Validar que el correo y código existan
        if not email or not codigo:
            return Response(
                {"error": "Debe enviar el correo y el código de verificación."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Buscar código en Redis
        stored_code = r.get(f"verify:{email}")
        if not stored_code:
            return Response(
                {"error": "El código ha expirado o no existe. Solicite uno nuevo."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Comparar código
        if stored_code != codigo:
            return Response(
                {"error": "El código ingresado no es correcto."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificación exitosa → eliminar código de Redis
        r.delete(f"verify:{email}")

        # Crear el usuario en la base de datos
        try:
            user = Usuario.objects.create(
                nombres=request.data.get("nombres"),
                apellidos=request.data.get("apellidos"),
                email=email,
                contrasena=request.data.get("contrasena"),
                apodo=request.data.get("apodo"),
                numerotelefono=request.data.get("numerotelefono"),
                tyc=request.data.get("tyc", True),
                estadocuenta="Activa",
                fechanacimiento=request.data.get("fechanacimiento"),
            )
        except Exception as e:
            return Response(
                {"error": f"No se pudo crear el usuario: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"message": "Cuenta verificada y usuario creado exitosamente."},
            status=status.HTTP_201_CREATED
        )


class LoginView(APIView):
    """
    Endpoint de login. Emite tokens JWT si las credenciales son válidas.
    """

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        contrasena = serializer.validated_data["contrasena"]

        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            return Response({"error": "Usuario no encontrado."}, status=404)

        if contrasena != user.contrasena:
            return Response({"error": "Contraseña incorrecta."}, status=400)

        user_proxy = UsuarioProxy.objects.get(pk=user.usuario_id)
        refresh = RefreshToken.for_user(user_proxy)
        return Response({
            "user": UsuarioSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=200)
