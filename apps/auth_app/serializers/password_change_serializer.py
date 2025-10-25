# apps/auth_app/serializers/password_change_serializer.py
"""
Serializer para cambio de contraseña de usuario autenticado.
Valida contraseña actual y nueva contraseña con políticas de seguridad.
"""

import logging
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

logger = logging.getLogger(__name__)


class PasswordChangeSerializer(serializers.Serializer):
    """
    Valida y cambia la contraseña del usuario autenticado.
    Requiere contraseña actual para verificación.
    """
    contrasena_actual = serializers.CharField(write_only=True)
    nueva_contrasena = serializers.CharField(write_only=True, min_length=8)

    def validate_nueva_contrasena(self, value):
        """
        Aplica validadores de contraseña de Django.
        """
        try:
            validate_password(value)
        except serializers.ValidationError:
            raise
        return value

    def validate_contrasena_actual(self, value):
        """
        Verifica que la contraseña actual sea correcta.
        """
        user = self.context["request"].user
        if not check_password(value, user.contrasena):
            raise serializers.ValidationError("La contraseña actual es incorrecta.")
        return value

    def validate(self, attrs):
        """
        Validaciones cruzadas: asegurar que nueva contraseña != actual.
        """
        contrasena_actual = attrs.get("contrasena_actual")
        nueva_contrasena = attrs.get("nueva_contrasena")

        if contrasena_actual == nueva_contrasena:
            raise serializers.ValidationError(
                {"nueva_contrasena": "La nueva contraseña debe ser diferente a la actual."}
            )

        return attrs

    def save(self):
        """
        Actualiza la contraseña del usuario en la base de datos.
        """
        user = self.context["request"].user
        nueva_contrasena = self.validated_data["nueva_contrasena"]

        # Hashear nueva contraseña
        user.contrasena = make_password(nueva_contrasena)
        user.save(update_fields=["contrasena"])

        logger.info(f"Contraseña cambiada para usuario {user.email}")
        return user