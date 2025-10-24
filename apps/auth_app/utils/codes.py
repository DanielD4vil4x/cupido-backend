# apps/auth_app/utils/codes.py
import random
import logging
from datetime import datetime

from apps.auth_app.utils.redis_client import (
    set_json,
    get_json,
    delete_key,
)

logger = logging.getLogger(__name__)

DEFAULT_CODE_TTL = 600  # 10 minutos
MAX_ATTEMPTS = 5


def generate_verification_code(email: str, ttl: int = DEFAULT_CODE_TTL) -> str:
    """
    Genera (o regenera) un código de 6 dígitos para `email`.
    Siempre sobrescribe cualquier código previo, resetea 'attempts' a 0
    y actualiza 'created_at'. Devuelve el nuevo código.
    """
    logger.info(f"Generando código de verificación para email: {email}")
    code = f"{random.randint(100000, 999999)}"
    logger.info(f"Código generado: {code}")
    key = f"verify:{email}"

    payload = {
        "code": code,
        "attempts": 0,
        "created_at": datetime.utcnow().isoformat(),
    }

    # set_json usa set / setex de Redis; esto sobrescribe el valor anterior
    logger.info(f"Guardando payload en Redis con clave: {key}")
    if set_json(key, payload, ttl=ttl):
        logger.info(f"Código de verificación generado (sobrescrito si existía) para {email}.")
        return code
    else:
        logger.error("No se pudo guardar el código en Redis.")
        raise RuntimeError("No se pudo guardar el código en Redis.")


# verify_code, invalidate_code, code_exists mantienen la misma lógica que antes.
def verify_code(email: str, user_code: str) -> bool:
    key = f"verify:{email}"
    data = get_json(key)
    if not data:
        logger.warning(f"Código expirado o no encontrado para {email}.")
        return False

    stored_code = data.get("code")
    attempts = data.get("attempts", 0)

    if attempts >= MAX_ATTEMPTS:
        logger.warning(f"Demasiados intentos para {email}. Código bloqueado.")
        delete_key(key)
        return False

    if user_code != stored_code:
        # Incrementar contador de intentos y resave con mismo ttl (esfuerzo simple)
        new_attempts = attempts + 1
        updated = {
            "code": stored_code,
            "attempts": new_attempts,
            "created_at": data.get("created_at"),
        }
        # Re-escribir manteniendo TTL por simplicidad (set_json usa ttl por defecto)
        set_json(key, updated, ttl=DEFAULT_CODE_TTL)
        logger.info(f"Código incorrecto para {email}. Intento {new_attempts}/{MAX_ATTEMPTS}.")
        return False

    # correcto: eliminar clave (consumir)
    delete_key(key)
    logger.info(f"Código validado correctamente para {email}.")
    return True


def invalidate_code(email: str) -> None:
    delete_key(f"verify:{email}")


def code_exists(email: str) -> bool:
    from apps.auth_app.utils.redis_client import key_exists
    return key_exists(f"verify:{email}")

