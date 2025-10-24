from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAccountActive(BasePermission):
    """
    Permite el acceso solo si la cuenta del usuario está activa.
    - Se usa junto con IsAuthenticated.
    - Evita que usuarios desactivados (soft delete o bloqueados) usen la API.
    """

    message = "Tu cuenta está inactiva. Contacta soporte para reactivarla."

    def has_permission(self, request, view):
        # Solo aplica si el usuario está autenticado
        user = request.user
        if not user or not user.is_authenticated:
            return False
        # Verifica flag de cuenta activa (por defecto Django usa user.is_active)
        return getattr(user, "is_active", False)


class IsOwnerOrAdmin(BasePermission):
    """
    Permite acceso si el usuario autenticado es el propietario del recurso
    o tiene privilegios de administrador (is_staff o is_superuser).

    Útil en endpoints tipo "perfil" o "cambiar contraseña".
    """

    message = "No tienes permiso para realizar esta acción."

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Permitir si el usuario es admin o superusuario
        if user and (user.is_staff or user.is_superuser):
            return True

        # Permitir si el usuario es el propietario del recurso
        # Se asume que el objeto tiene un atributo 'user' o 'owner'
        owner = getattr(obj, "user", None) or getattr(obj, "owner", None)
        return owner == user

    def has_permission(self, request, view):
        """
        Permitir acceso global a métodos seguros (GET, HEAD, OPTIONS)
        y dejar la comprobación por objeto para métodos de modificación.
        """
        if request.method in SAFE_METHODS:
            return True
        return True  # La verificación detallada se hace en has_object_permission()

