from django.db import models
from legacy_models.models import Usuario

class UsuarioProxy(Usuario):
    """
    Proxy model que expone 'id' como alias de 'usuario_id'
    para compatibilidad con SimpleJWT y otros módulos.
    """
    class Meta:
        proxy = True

    @property
    def id(self):
        return self.usuario_id
