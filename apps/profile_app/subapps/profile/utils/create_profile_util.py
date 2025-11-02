# apps/profile_app/subapps/profile/utils/create_profile_util.py

from django.utils import timezone
from ..models import Perfil
from apps.auth_app.models import Ubicacion


def create_profile_for_user(user):
    """
    Crea un perfil automáticamente para el usuario con valores por defecto.

    Args:
        user: Instancia del modelo Usuario

    Returns:
        Perfil: Instancia del perfil creado
    """
    # Obtener ubicación por defecto 'Pamplona'
    ubicacion_default = Ubicacion.objects.filter(descripcion='Pamplona').first()

    perfil = Perfil.objects.create(
        usuario=user,
        programa_academico=None,  # empty
        ubicacion=ubicacion_default,
        hobbies=None,  # empty
        estatura=None,  # empty
        estado='Encupidado',  # default
        fecharegistro=timezone.now()
    )

    return perfil