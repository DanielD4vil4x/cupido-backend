# apps/auth_app/utils/tokens.py

from rest_framework_simplejwt.tokens import RefreshToken
import logging

logger = logging.getLogger(__name__)

def create_jwt_for_user(user) -> dict:
    """
    Genera tokens JWT (access + refresh) para usuarios legacy (sin registro en OutstandingToken).
    """
    try:
        refresh = RefreshToken.for_user(user)
        tokens = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
        logger.info(f"🎫 Tokens generados correctamente para usuario ID {user.pk}")
        return tokens
    except Exception as e:
        logger.error(f"❌ Error al generar tokens JWT: {e}")
        raise


def blacklist_token(refresh_token: str) -> bool:
    """
    Invalida un token refresh (lo agrega a la lista negra si está habilitada).
    """
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()  # Solo si SIMPLE_JWT['BLACKLIST_AFTER_ROTATION'] = True
        logger.info("🔒 Token refresh agregado a la lista negra correctamente.")
        return True
    except Exception as e:
        logger.warning(f"⚠️ No se pudo invalidar el token: {e}")
        return False
