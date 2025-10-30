# apps/auth_app/utils/user_get.py

from apps.auth_app.utils.profile import compute_account_state
from apps.auth_app.serializers.user_get_serializer import serialize_user_profile
from apps.auth_app.models import Usuario


def get_user_profile_data(user: Usuario) -> dict:
    """
    Obtiene todos los datos del perfil del usuario y calcula su estado.
    Mantiene sincronizado el campo estadocuenta si difiere del estado calculado.
    
    Returns:
        dict: Contiene 'estado', 'should_complete_profile' y 'user' con todos los campos
    """
    estado = compute_account_state(user)
    
    # Mantener sincronizado con el campo persistido si difiere
    if getattr(user, "estadocuenta", None) != estado:
        user.estadocuenta = estado
        user.save(update_fields=["estadocuenta"])
    
    # Serializar todos los campos del usuario
    user_data = serialize_user_profile(user)
    
    return {
        "estado": estado,
        "should_complete_profile": estado == "incompleta",
        "user": user_data,
    }

