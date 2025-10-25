# apps/auth_app/serializers/deactivate_serializer.py
"""
Serializer para desactivación de cuenta de usuario.
Requiere confirmación de contraseña para seguridad.
"""

import logging
from django.contrib.auth.hashers import check_password
from rest_framework import serializers

logger = logging.getLogger(__name__)


class DeactivateAccountSerializer(serializers.Serializer):
    """
    Valida contraseña actual antes de permitir desactivación de cuenta.
    Cambia estadocuenta a 'Inactiva' (soft delete).
    """
    contrasena = serializers.CharField(write_only=True)
    confirmacion = serializers.CharField(write_only=True)  # Para confirmar intención

    def validate_contrasena(self, value):
        """
        Verifica que la contraseña actual sea correcta.
        """
        user = self.context["request"].user
        if not check_password(value, user.contrasena):
            raise serializers.ValidationError("Contraseña incorrecta.")
        return value

    def validate_confirmacion(self, value):
        """
        Verifica que el usuario confirme la desactivación.
        """
        if value.lower() not in ["desactivar", "confirmar", "si"]:
            raise serializers.ValidationError(
                "Debe escribir 'desactivar', 'confirmar' o 'si' para proceder."
            )
        return value

    def save(self):
        """
        Desactiva la cuenta cambiando estadocuenta a 'Inactiva'.
        """
        user = self.context["request"].user
        user.estadocuenta = "Inactiva"
        user.save(update_fields=["estadocuenta"])

        logger.info(f"Cuenta desactivada para usuario {user.email}")
        return user