# apps/auth_app/utils/recaptcha.py
"""
Verifica tokens reCAPTCHA v2 con Google.
Optimizado para producción con manejo robusto de errores.
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

    Raises:
        RuntimeError: Si hay problemas de conectividad con Google reCAPTCHA.
    """
    # Validar que el token no esté vacío
    if not token or not token.strip():
        logger.warning("Token reCAPTCHA vacío o inválido recibido")
        return False, {"success": False, "error-codes": ["missing-input-response"]}

    secret_key = getattr(settings, "RECAPTCHA_SECRET_KEY", None)
    if not secret_key:
        logger.error("RECAPTCHA_SECRET_KEY no configurada en settings")
        raise ImproperlyConfigured("RECAPTCHA_SECRET_KEY no está configurada en settings.")

    verify_url = "https://www.google.com/recaptcha/api/siteverify"

    try:
        logger.info("Verificando reCAPTCHA con Google...")
        response = requests.post(
            verify_url,
            data={"secret": secret_key, "response": token},
            timeout=15,  # Timeout generoso para producción
            headers={"User-Agent": "Cupido-Backend/1.0"}
        )
        response.raise_for_status()
        result = response.json()
        success = result.get("success", False)

        if success:
            logger.info("reCAPTCHA verificado exitosamente")
        else:
            error_codes = result.get("error-codes", [])
            logger.warning(f"reCAPTCHA falló - Códigos de error: {error_codes}")

        return success, result

    except requests.Timeout:
        logger.error("Timeout al conectar con Google reCAPTCHA - Revisa conectividad de red")
        raise RuntimeError("No se pudo verificar reCAPTCHA (timeout). Intenta nuevamente.")

    except requests.HTTPError as e:
        logger.error(f"Error HTTP al verificar reCAPTCHA: {e.response.status_code}")
        raise RuntimeError("Error al comunicarse con el servicio de reCAPTCHA.")

    except requests.RequestException as e:
        logger.error(f"Error de red al verificar reCAPTCHA: {type(e).__name__} - {str(e)}")
        raise RuntimeError("Error de conexión al verificar reCAPTCHA. Verifica tu conexión.")

    except Exception as e:
        logger.error(f"Error inesperado al verificar reCAPTCHA: {type(e).__name__} - {str(e)}")
        raise RuntimeError("Error inesperado al verificar reCAPTCHA.")

