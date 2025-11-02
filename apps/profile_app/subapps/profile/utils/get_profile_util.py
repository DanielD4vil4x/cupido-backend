# apps/profile_app/subapps/profile/utils/get_profile_util.py

from ..models import Perfil


def get_profile_data(user):
    """
    Obtiene los datos del perfil del usuario.

    Args:
        user: Instancia del modelo Usuario

    Returns:
        Perfil or None: Instancia del perfil si existe, None si no
    """
    try:
        perfil = Perfil.objects.get(usuario=user)
        return perfil
    except Perfil.DoesNotExist:
        return None