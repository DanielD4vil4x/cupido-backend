# Puedes usar este archivo para proxy models si necesitas lógica adicional
# sobre tus modelos de legacy_models.

from legacy_models.models import Usuario

class UsuarioProxy(Usuario):
    class Meta:
        proxy = True
        verbose_name = "Usuario Proxy"
        verbose_name_plural = "Usuarios Proxy"
