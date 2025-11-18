# apps/auth_app/utils/recaptcha.py
"""
Verifica tokens reCAPTCHA v2 con Google.
"""

import requests
import logging
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


def verify_recaptcha_token(token: str) -> tuple[bool, dict]:
    """
    Verifica un token reCAPTCHA v2 con el endpoint oficial de Google.

    Args:
        token (str): Token enviado desde el frontend (g-recaptcha-response).

    Returns:
        tuple: (success: bool, details: dict)
    """
    secret_key = getattr(settings, "RECAPTCHA_SECRET_KEY", None)
    if not secret_key:
        raise ImproperlyConfigured("RECAPTCHA_SECRET_KEY no está configurada en settings.")

    verify_url = "https://www.google.com/recaptcha/api/siteverify"

    try:
        response = requests.post(
            verify_url,
            data={"secret": secret_key, "response": token},
            timeout=5,
        )
        response.raise_for_status()
        result = response.json()
        success = result.get("success", False)

        if success:
            logger.info("✅ reCAPTCHA verificado exitosamente")
        else:
            logger.warning(f"❌ reCAPTCHA falló: {result.get('error-codes', [])}")

        return success, result
    except requests.RequestException as e:
        logger.error(f"⚠️ Error de conexión con reCAPTCHA: {e}")
        raise RuntimeError(f"Error al verificar reCAPTCHA: {e}")

