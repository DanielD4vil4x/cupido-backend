from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from legacy_models.models import Usuario
from rest_framework_simplejwt.tokens import RefreshToken
from apps.auth_app.serializers.auth import LoginSerializer, UsuarioSerializer

class RegisterView(APIView):
    """
    Endpoint de registro con validación de correo institucional.
    (La verificación real se hace en verification.py)
    """
    def post(self, request):
        email = request.data.get("email")
        nombre = request.data.get("nombre")

        if not email or not email.endswith("@unipamplona.edu.co"):
            return Response({"error": "Debe usar un correo institucional."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Validar si ya existe
        if Usuario.objects.filter(correo=email).exists():
            return Response({"error": "El usuario ya está registrado."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Crear registro en base de datos (ajusta según tu esquema legacy)
        user = Usuario.objects.create(
            nombre=nombre,
            correo=email,
            verificado=False,
        )
        return Response({"message": "Usuario creado, verifique su correo institucional."}, status=201)


class LoginView(APIView):
    """
    Endpoint de login. Emite tokens JWT si las credenciales son válidas.
    """
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        try:
            user = Usuario.objects.get(correo=email)
        except Usuario.DoesNotExist:
            return Response({"error": "Usuario no encontrado."}, status=404)

        # En tu base legacy puede que no manejes contraseñas aún,
        # así que esto puede ajustarse cuando agregues hashing o auth real.
        if password != "123456":  # placeholder
            return Response({"error": "Contraseña incorrecta."}, status=400)

        refresh = RefreshToken.for_user(user)
        return Response({
            "user": UsuarioSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=200)



