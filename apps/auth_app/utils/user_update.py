# apps/auth_app/utils/user_update.py

from apps.auth_app.utils.profile import is_profile_complete
from apps.auth_app.models import Usuario


def update_user_profile_completion_status(user: Usuario) -> None:
    """
    Actualiza el estado de completitud del perfil del usuario.
    Si el perfil ahora cumple los mínimos, actualiza estadocuenta a 'completa'.
    """
    if is_profile_complete(user) and user.estadocuenta != "0":
        user.estadocuenta = "2"
        user.save(update_fields=["estadocuenta"])


def get_user_update_response_data(user: Usuario) -> dict:
    """
    Genera la respuesta estándar para actualizaciones de perfil.
    Incluye mensaje de éxito, estado actual y datos básicos del usuario.
    
    Returns:
        dict: Respuesta estructurada para PATCH /user-update/
    """
    return {
        "message": "Perfil actualizado correctamente.",
        "estado": user.estadocuenta,
        "user": {
            "usuario_id": user.usuario_id,
            "nombres": user.nombres,
            "apellidos": user.apellidos,
            "email": user.email,
            "genero": user.genero.genero_id if user.genero else None,
            "genero_descripcion": user.genero.descripcion if user.genero else None,
            "fechanacimiento": user.fechanacimiento,
            "descripcion": user.descripcion,
            "estadocuenta": user.estadocuenta,
            "numerotelefono": user.numerotelefono,
        },
    }

