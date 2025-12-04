# apps/auth_app/serializers/password_reset_serializer.py
"""
Serializers para recuperación de contraseña.
- PasswordResetRequestSerializer: Solicita recuperación enviando email con token
- PasswordResetConfirmSerializer: Confirma recuperación con token y nueva contraseña
"""

import logging
import uuid
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from django.conf import settings
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
        Genera token único, lo guarda en Redis y envía email con enlace.
        Siempre responde OK por seguridad (no revela si email existe).
        """
        email = self.validated_data["email"]

        # Verificar si el usuario existe antes de enviar nada
        try:
            Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            # Si no existe, no hacemos nada, pero retornamos éxito para no revelar información
            logger.info(f"Solicitud de recuperación para email no existente: {email}")
            return

        # Generar token único (UUID)
        reset_token = str(uuid.uuid4())

        # Guardar token en Redis con clave especial
        redis_key = f"reset_token:{reset_token}"
        set_json(redis_key, {"email": email, "used": False}, ttl=RESET_TOKEN_TTL)

        # Construir enlace de restablecimiento
        frontend_url = "https://cupidocol.com/"
        reset_link = f"{frontend_url}reset-password?token={reset_token}"

        # Enviar email (si el usuario existe, pero no verificamos aquí)
        try:
            email_utils.send_password_reset_email(email, reset_link)
            logger.info(f"Email de recuperación enviado a {email}")
        except Exception as e:
            logger.error(f"Error enviando email de recuperación a {email}: {e}")
            # No fallamos aquí por seguridad


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Valida token de recuperación y nueva contraseña.
    Actualiza la contraseña del usuario si todo es válido.
    """
    token = serializers.CharField(min_length=36, max_length=36)
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

    def validate(self, attrs):
        token = attrs.get("token")

        # Verificar token en Redis
        redis_key = f"reset_token:{token}"
        reset_data = get_json(redis_key)
        if not reset_data:
            raise serializers.ValidationError({"token": "Token expirado o inválido."})

        if reset_data.get("used", False):
            raise serializers.ValidationError({"token": "Token ya utilizado."})

        email = reset_data.get("email")
        if not email:
            raise serializers.ValidationError({"token": "Token inválido."})

        # Verificar que el usuario existe
        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError({"token": "Usuario no encontrado."})

        attrs["user"] = user
        attrs["token_key"] = redis_key
        return attrs

    def save(self):
        """
        Actualiza la contraseña del usuario y marca el token como usado.
        """
        user = self.validated_data["user"]
        nueva_contrasena = self.validated_data["nueva_contrasena"]
        token_key = self.validated_data["token_key"]

        # Hashear nueva contraseña
        user.contrasena = make_password(nueva_contrasena)
        user.save(update_fields=["contrasena"])

        # Marcar token como usado
        reset_data = get_json(token_key)
        if reset_data:
            reset_data["used"] = True
            set_json(token_key, reset_data, ttl=RESET_TOKEN_TTL)  # Mantener TTL

        logger.info(f"Contraseña restablecida para usuario {user.email}")
        return user
