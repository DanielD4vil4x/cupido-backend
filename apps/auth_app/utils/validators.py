# apps/auth_app/utils/validators.py
"""
Utilidades de validación compartidas entre serializers y vistas.
Incluye validaciones para:
 - Correos institucionales (@unipamplona.edu.co)
 - Cálculo de edad mínima
"""

import re
from datetime import date
from rest_framework import serializers


INSTITUTIONAL_DOMAIN = "@unipamplona.edu.co"


def validate_institutional_email(email: str) -> bool:
    """
    Verifica que el email pertenezca al dominio institucional válido.
    Lanza ValidationError si no cumple.

    Args:
        email (str): correo a validar.
    Returns:
        bool: True si es válido.
    """
    if not email or "@" not in email:
        raise serializers.ValidationError("Correo electrónico inválido.")

    if not email.endswith(INSTITUTIONAL_DOMAIN):
        raise serializers.ValidationError(
            f"Debe usar un correo institucional {INSTITUTIONAL_DOMAIN}."
        )

    # Validar estructura general del correo
    pattern = r"^[a-zA-Z0-9._%+-]+@unipamplona\.edu\.co$"
    if not re.match(pattern, email):
        raise serializers.ValidationError("Formato de correo institucional inválido.")

    return True


def calculate_age(birth_date: date) -> int:
    """
    Calcula la edad exacta de un usuario dada su fecha de nacimiento.
    Args:
        birth_date (date): fecha de nacimiento.
    Returns:
        int: edad en años.
    """
    if not isinstance(birth_date, date):
        raise ValueError("Se esperaba un objeto datetime.date válido.")

    today = date.today()
    age = today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )
    return age
