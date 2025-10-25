# apps/auth_app/serializers/verify_serializer.py
from rest_framework import serializers
from datetime import date

from apps.auth_app.utils.validators import validate_institutional_email
from apps.auth_app.utils import codes
from apps.auth_app.utils.redis_client import get_json

class VerifyEmailSerializer(serializers.Serializer):
    """
    Valida el email y el código enviado por el usuario para completar
    el registro (verificación). No crea el usuario; solo valida que:
      - el email tenga formato institucional
      - exista un registro temporal en Redis (register:{email})
      - el código coincida con el código generado (codes.verify_code)

    Uso típico:
      serializer = VerifyEmailSerializer(data=request.data)
      serializer.is_valid(raise_exception=True)
      payload = serializer.get_registration_payload()  # datos listos para crear usuario
    """

    email = serializers.EmailField()
    codigo = serializers.CharField(write_only=True, min_length=6, max_length=10)

    def validate_email(self, value):
        # Validar dominio institucional y formato
        try:
            validate_institutional_email(value)
        except serializers.ValidationError:
            raise
        except Exception:
            # fallback mínimo
            if not value.endswith("@unipamplona.edu.co"):
                raise serializers.ValidationError("Debe usar un correo institucional @unipamplona.edu.co.")
        return value

    def validate_codigo(self, value):
        # Normalizar (eliminar espacios) y validar formato numérico simple
        code = value.strip()
        if not code.isdigit():
            raise serializers.ValidationError("El código de verificación debe ser numérico.")
        if len(code) < 4:
            raise serializers.ValidationError("Código de verificación demasiado corto.")
        return code

    def validate(self, attrs):
        """
        Validación cruzada:
         - Comprobar que exista un payload temporal de registro en Redis
         - Verificar el código a través del módulo codes (verify_code)
        """

        email = attrs.get("email")
        codigo = attrs.get("codigo")

        # 1) Verificar que exista un registro temporal
        redis_key = f"register:{email}"
        registration_payload = get_json(redis_key)
        if not registration_payload:
            raise serializers.ValidationError({
                "email": "No existe un registro previo para este correo o ha expirado. Por favor regístrate de nuevo."
            })

        # 2) Verificar código con la utilidad de códigos
        try:
            valid = codes.verify_code(email, codigo)
        except Exception as e:
            raise serializers.ValidationError({"codigo": "Error al verificar el código. Intenta de nuevo más tarde."})

        if not valid:
            raise serializers.ValidationError({"codigo": "Código inválido o ha expirado."})

        # almacenar payload para que get_registration_payload lo devuelva
        self._registration_payload = registration_payload

        return attrs

    def get_registration_payload(self) -> dict:
        """
        Devuelve el payload (dict) almacenado en Redis correspondiente al email validado.
        Debe llamarse sólo después de `is_valid()`.
        El payload es el que se utilizará para crear el usuario en la base de datos.
        """
        if not hasattr(self, "_registration_payload"):
            raise RuntimeError("Llama a is_valid() antes de usar get_registration_payload().")
        return dict(self._registration_payload)  # devolver copia para evitar mutaciones
