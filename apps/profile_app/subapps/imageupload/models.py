from django.db import models
from apps.auth_app.models import Usuario

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f'user_{instance.usuario.usuario_id}/{filename}'

class Imagen(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to=user_directory_path)
    es_principal = models.BooleanField(default=False)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Imagen"
        verbose_name_plural = "Imagenes"
        ordering = ['-fecha_subida']

    def __str__(self):
        return f"Imagen de {self.usuario.email} subida el {self.fecha_subida.strftime('%Y-%m-%d')}"
