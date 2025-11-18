# apps/auth_app/serializers/password_reset_serializer.py
"""
Serializers para recuperación de contraseña.
- PasswordResetRequestSerializer: Solicita recuperación enviando email con token
- PasswordResetConfirmSerializer: Confirma recuperación con token y nueva contraseña
"""

import logging
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from apps.auth_app.models import Usuario

from apps.auth_app.utils.validators import validate_institutional_email
from apps.auth_app.utils.redis_client import set_json, get_json, delete_key
from apps.auth_app.utils import email_utils

logger = logging.getLogger(__name__)

RESET_TOKEN_TTL = 1800  


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Valida email institucional y envía token de recuperación por correo.
    No revela si el email existe por seguridad.
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        """
        Valida formato institucional, pero no verifica existencia para evitar enumeración.
        """
        try:
            validate_institutional_email(value)
        except serializers.ValidationError:
            raise
        except Exception:
            if not value.endswith("@unipamplona.edu.co"):
                raise serializers.ValidationError("Debe usar un correo institucional @unipamplona.edu.co.")
        return value

    def save(self):
        """
        Genera token único, lo guarda en Redis y envía email.
        Siempre responde OK por seguridad (no revela si email existe).
        """
        email = self.validated_data["email"]

        # Generar token único (usamos el mismo generador de códigos)
        from apps.auth_app.utils.codes import generate_verification_code
        reset_token = generate_verification_code(email, ttl=RESET_TOKEN_TTL)

        # Guardar token en Redis con clave especial
        redis_key = f"reset:{email}"
        set_json(redis_key, {"token": reset_token}, ttl=RESET_TOKEN_TTL)

        # Enviar email (si el usuario existe, pero no verificamos aquí)
        try:
            email_utils.send_password_reset_email(email, reset_token)
            logger.info(f"Email de recuperación enviado a {email}")
        except Exception as e:
            logger.error(f"Error enviando email de recuperación a {email}: {e}")
            # No fallamos aquí por seguridad


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Valida token de recuperación y nueva contraseña.
    Actualiza la contraseña del usuario si todo es válido.
    """
    email = serializers.EmailField()
    token = serializers.CharField(min_length=6, max_length=10)
    nueva_contrasena = serializers.CharField(write_only=True, min_length=8)

    def validate_email(self, value):
        try:
            validate_institutional_email(value)
        except serializers.ValidationError:
            raise
        except Exception:
            if not value.endswith("@unipamplona.edu.co"):
                raise serializers.ValidationError("Debe usar un correo institucional @unipamplona.edu.co.")
        return value

    def validate_nueva_contrasena(self, value):
        """
        Aplica validadores de contraseña de Django.
        """
        try:
            validate_password(value)
        except serializers.ValidationError:
            raise
        return value

    def validate(self, attrs):
        email = attrs.get("email")
        token = attrs.get("token")

        # Verificar token en Redis
        redis_key = f"reset:{email}"
        reset_data = get_json(redis_key)
        if not reset_data:
            raise serializers.ValidationError({"token": "Token expirado o inválido."})

        stored_token = reset_data.get("token")
        if token != stored_token:
            raise serializers.ValidationError({"token": "Token incorrecto."})

        # Verificar que el usuario existe
        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError({"email": "Usuario no encontrado."})

        attrs["user"] = user
        return attrs

    def save(self):
        """
        Actualiza la contraseña del usuario y elimina el token.
        """
        user = self.validated_data["user"]
        nueva_contrasena = self.validated_data["nueva_contrasena"]
        email = self.validated_data["email"]

        # Hashear nueva contraseña
        user.contrasena = make_password(nueva_contrasena)
        user.save(update_fields=["contrasena"])

        # Eliminar token de Redis
        delete_key(f"reset:{email}")

        logger.info(f"Contraseña restablecida para usuario {email}")
        return user