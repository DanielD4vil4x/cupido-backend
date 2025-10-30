# apps/auth_app/serializers/resend_serializer.py
from rest_framework import serializers
from apps.auth_app.utils.validators import validate_institutional_email
from apps.auth_app.models import Usuario

class ResendCodeSerializer(serializers.Serializer):
    """
    Valida el email (y opcional recaptcha_token si lo quieres) para reenviar
    el código de verificación.
    """
    email = serializers.EmailField()
    # Si en tu frontend quieres reCAPTCHA en resend también, descomenta:
    # recaptcha_token = serializers.CharField(write_only=True, required=False)

    def validate_email(self, value):
        # validar dominio institucional
        try:
            validate_institutional_email(value)
        except serializers.ValidationError:
            raise
        except Exception:
            if not value.endswith("@unipamplona.edu.co"):
                raise serializers.ValidationError("Debe usar un correo institucional @unipamplona.edu.co.")
        # Si ya existe un usuario final creado (registro completo), no permitir resend
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("El correo ya está registrado. Usa iniciar sesión o recuperar contraseña.")
        return value
