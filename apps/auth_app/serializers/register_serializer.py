# apps/auth_app/serializers/register_serializer.py
from datetime import date

from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from legacy_models.models import Usuario

# Utilidades (implementarlas en apps.auth_app.utils)
from apps.auth_app.utils.recaptcha import verify_recaptcha_token
from apps.auth_app.utils.validators import (
    validate_institutional_email,
    calculate_age,
)


class RegisterSerializer(serializers.Serializer):
    """
    Valida datos del registro inicial. No crea el usuario: prepara datos limpios
    listos para guardarse temporalmente en Redis (o en la vista).
    Campos esperados (según la BD legacy):
      - email, nombres, apellidos, fechanacimiento, contrasena, sexo, programa, tyc

    Requisitos realizados aquí:
      * Validación token reCaptcha (campo: recaptcha_token)
      * Validación formato y dominio de email institucional
      * Verificar que el email no exista ya en la tabla Usuario
      * Validación de edad; añade 'estadocuenta' = 'Menor' o 'Activa'
      * Aplicar validadores de contraseña de Django
      * Nunca devuelve ni almacena la contraseña en texto claro (usamos make_password)
    """

    email = serializers.EmailField()
    nombres = serializers.CharField(max_length=150)
    apellidos = serializers.CharField(max_length=150)
    fechanacimiento = serializers.DateField()
    contrasena = serializers.CharField(write_only=True, min_length=8)
    sexo = serializers.CharField(allow_blank=True, required=False)
    programa = serializers.CharField(allow_blank=True, required=False)
    tyc = serializers.BooleanField()
    recaptcha_token = serializers.CharField(write_only=True)

    def validate_recaptcha_token(self, value):
        print("Token recibido:", value)
        try:
            success, details = verify_recaptcha_token(value)
            print("Respuesta de Google:", details)
        except Exception as e:
            raise serializers.ValidationError(f"Error validando reCAPTCHA: {str(e)}")

        if not success:
            error_codes = details.get("error-codes", [])
            raise serializers.ValidationError(f"reCAPTCHA inválido. Códigos: {error_codes}")
    
        return value

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

    def validate_fechanacimiento(self, value):
        """
        Calcula la edad con calculate_age (utils). Acepta fechas válidas.
        """
        # fecha en el futuro no permitida
        if value > date.today():
            raise serializers.ValidationError("La fecha de nacimiento no puede estar en el futuro.")

        try:
            age = calculate_age(value)
        except Exception:
            # fallback simple
            today = date.today()
            age = int((today - value).days / 365.25)

        if age < 0:
            raise serializers.ValidationError("Fecha de nacimiento inválida.")
        # podemos devolver la fecha, el cálculo se hace en validate() para setear estadocuenta
        return value

    def validate_tyc(self, value):
        """
        El frontend obliga a enviar tyc=True. Reforzamos en backend.
        """
        if not value:
            raise serializers.ValidationError("Debe aceptar los términos y condiciones.")
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
         - calcular edad y definir estadocuenta
         - cualquier validación adicional que requiera varios campos
        """
        fechanacimiento = attrs.get("fechanacimiento")
        # calcular edad robustamente (usar util si disponible)
        try:
            age = calculate_age(fechanacimiento)
        except Exception:
            today = date.today()
            age = int((today - fechanacimiento).days / 365.25)

        # decidir estado de cuenta
        if age < 18:
            attrs["estadocuenta"] = "Menor"
        else:
            attrs["estadocuenta"] = "Activa"

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
            data["contrasena"] = make_password(raw_pass)
        # añadir un flag temporal opcional
        data["_from_registration"] = True
        return data

