from datetime import date

from apps.auth_app.models import Usuario


REQUIRED_COMPLETION_FIELDS = [
    "nombres",
    "apellidos",
    "genero",
    "fechanacimiento",
    "descripcion",
]

def is_profile_complete(user: Usuario) -> bool:
    """
    Determina si el perfil del usuario está completo con base en campos mínimos.
    Evita valores dummy creados durante la verificación inicial.
    
    Campos requeridos:
    - nombres (no dummy)
    - apellidos (no dummy)
    - genero (debe estar establecido)
    - fechanacimiento (válida)
    - descripcion (opcional, puede estar vacía)
    """
    if not isinstance(user, Usuario):
        return False

    if not user.nombres or user.nombres.strip().lower() == "dummy":
        return False
    if not user.apellidos or user.apellidos.strip().lower() == "dummy":
        return False
    if not user.genero:
        return False
    if not user.fechanacimiento or user.fechanacimiento >= date.today():
        return False

    return True


def compute_account_state(user: Usuario) -> str:
    """
    Devuelve "completa" si el perfil cumple mínimos, en caso contrario "incompleta".
    """
    return "2" if is_profile_complete(user) else "1"



    


