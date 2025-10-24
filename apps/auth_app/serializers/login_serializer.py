# apps/auth_app/serializers/login_serializer.py

from django.contrib.auth.hashers import check_password
from rest_framework import serializers
from legacy_models.models import Usuario


class LoginSerializer(serializers.Serializer):
    """
    Valida credenciales de inicio de sesión.
    - Comprueba existencia del usuario.
    - Verifica la contraseña (con hash).
    - Bloquea acceso si el usuario tiene estadocuenta = 'Menor'.
    """

    email = serializers.EmailField()
    contrasena = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        contrasena = attrs.get("contrasena")

        # 1️⃣ Verificar existencia del usuario
        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError({"email": "Usuario no encontrado."})

        # 2️⃣ Verificar estado de cuenta (mayoría de edad)
        if user.estadocuenta == "Menor":
            raise serializers.ValidationError(
                {"email": "No se permite el acceso a menores de edad."}
            )

        # 3️⃣ Validar contraseña (verificación segura con hash)
        if not check_password(contrasena, user.contrasena):
            raise serializers.ValidationError({"contrasena": "Contraseña incorrecta."})

        # 4️⃣ Si todo es correcto, adjuntar usuario validado
        attrs["user"] = user
        return attrs
