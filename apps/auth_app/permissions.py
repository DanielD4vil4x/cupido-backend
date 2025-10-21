from rest_framework import permissions

class IsVerifiedUser(permissions.BasePermission):
    """
    Permite el acceso solo a usuarios con el campo 'verificado' = True
    (o ajusta según tu modelo legacy).
    """
    def has_permission(self, request, view):
        user = request.user
        return getattr(user, "verificado", False)
