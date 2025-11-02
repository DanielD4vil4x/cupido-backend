from apps.profile_app.subapps.profile.models import Perfil

def get_or_create_user_profile(user):
    """
    Retorna el perfil del usuario si existe, o lo crea si no.
    """
    perfil, created = Perfil.objects.get_or_create(usuario=user)
    return perfil
