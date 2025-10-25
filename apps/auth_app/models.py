from django.db import models
from legacy_models.models import Usuario

class UsuarioProxy(Usuario):
    """
    Proxy del modelo 'legacy_models.Usuario' que mantiene la misma tabla
    pero expone 'id' como alias de 'usuario_id' para compatibilidad con:
      - SimpleJWT
      - request.user.id
      - DRF serializers
    No crea una tabla nueva en la base de datos.
    """

    class Meta:
        proxy = True
        verbose_name = "Usuario (proxy)"
        verbose_name_plural = "Usuarios (proxy)"

    @property
    def id(self):
        """Alias de 'usuario_id' para compatibilidad con librerías modernas."""
        return self.usuario_id

    def __str__(self):
        """Representación legible en admin/logs."""
        return f"{getattr(self, 'nombre', '')} ({getattr(self, 'email', '')})"

