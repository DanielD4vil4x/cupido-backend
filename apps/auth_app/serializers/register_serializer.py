# apps/auth_app/serializers/register_serializer.py

from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from datetime import date
from django.utils import timezone

from apps.auth_app.models import Usuario, Programa, Genero

# Utilidades (implementarlas en apps.auth_app.utils)
from apps.auth_app.utils.recaptcha import verify_recaptcha_token
from apps.auth_app.utils.validators import validate_institutional_email, calculate_age


class RegisterSerializer(serializers.Serializer):
    """
    Valida datos mínimos del registro inicial. No crea el usuario: prepara datos limpios
    listos para guardarse temporalmente en Redis.

    Campos requeridos según especificaciones:
      - email (institucional @unipamplona.edu.co)
      - contrasena (con validaciones de seguridad)
      - recaptcha_token
      - tyc (términos y condiciones)
      - firma (firma del usuario)

    Requisitos realizados aquí:
      * Validación token reCaptcha
      * Validación formato y dominio de email institucional
      * Verificar que el email no exista ya en la tabla Usuario
      * Aplicar validadores de contraseña de Django
      * Nunca devuelve ni almacena la contraseña en texto claro (usamos make_password)
      * Establece 'estadocuenta' por defecto a 'incompleta'
    """

    # Campos obligatorios
    recaptcha_token = serializers.CharField(write_only=True, required=True, allow_blank=False)
    email = serializers.EmailField()
    contrasena = serializers.CharField(write_only=True, min_length=8)
    tyc = serializers.BooleanField()
    firma = serializers.CharField(required=True, allow_blank=False)

    def validate_recaptcha_token(self, value):
        """
        Validar reCAPTCHA (DRF valida en orden de declaración de campos).
        Maneja específicamente tokens expirados.
        """
        try:
            success, details = verify_recaptcha_token(value)
            if not success:
                error_codes = details.get("error-codes", [])

                # Mensaje específico para token expirado
                if "timeout-or-duplicate" in error_codes:
                    raise serializers.ValidationError(
                        "El reCAPTCHA ha expirado. Por favor, completa el reCAPTCHA nuevamente."
                    )

                # Otros errores de reCAPTCHA
                raise serializers.ValidationError(f"reCAPTCHA inválido. Códigos: {error_codes}")
            return value
        except RuntimeError as e:
            raise serializers.ValidationError(str(e))

    def validate_email(self, value):
        """
        Verifica dominio institucional y unicidad en legacy Usuario.
        Reutiliza validate_institutional_email (utils) para chequear formato/domain.
        """
        # validar dominio/estructura institucional
        try:
            validate_institutional_email(value)
        except serializers.ValidationError:
            raise
        except Exception:
            # si la util no existe o falla, caer en fallback simple
            if not value.endswith("@unipamplona.edu.co"):
                raise serializers.ValidationError("Debe usar correo institucional @unipamplona.edu.co.")

        # verificar unicidad en legacy table
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("El correo ya se encuentra registrado.")
        return value

    def validate_contrasena(self, value):
        """
        Aplicar validadores de contraseña de Django (longitud, similaridad, etc.)
        """
        try:
            validate_password(value)
        except serializers.ValidationError:
            # Re-lanzar en formato de serializer
            raise
        return value

    def validate(self, attrs):
        """
        Validaciones cruzadas:
          - Establecer estadocuenta por defecto a 'incompleta'
          - Establecer fecharegistro por defecto
          - cualquier validación adicional que requiera varios campos
        """
        # Establecer estado de cuenta por defecto
        attrs["estadocuenta"] = "1"

        # Establecer fecha de registro por defecto (se puede actualizar luego)
        attrs["fecharegistro"] = timezone.now()

        # No incluimos recaptcha_token en payload final (no lo almacenamos)
        attrs.pop("recaptcha_token", None)

        return attrs

    def to_redis_payload(self):
        """
        Prepara un dict con los datos que se deben guardar temporalmente en Redis.
        Important: no incluye campos sensibles en texto plano.
        - contrasena: se devuelve hasheada con make_password
        - incluye un campo meta para saber que viene del registro
        """
        if not hasattr(self, "validated_data"):
            raise RuntimeError("Debe llamar is_valid() antes de to_redis_payload().")

        data = dict(self.validated_data)  # copia segura
        raw_pass = data.pop("contrasena", None)
        # Nunca guardar raw password en Redis: hashearla
        if raw_pass:
            data["password"] = make_password(raw_pass)  # Cambiar a "password" para compatibilidad con AbstractUser
        # añadir un flag temporal opcional
        data["_from_registration"] = True
        return data