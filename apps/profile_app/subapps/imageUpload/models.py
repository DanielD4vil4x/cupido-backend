from django.db import models
from apps.auth_app.models import Usuario
import os
import uuid

def user_directory_path(instance, filename):
    """Nombre temporal único - se renombrará después con el ID real"""
    extension = filename.split('.')[-1].lower()
    # Nombre temporal con UUID
    return f"temp_{uuid.uuid4().hex[:8]}.{extension}"

class Imagen(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to=user_directory_path)
    es_principal = models.BooleanField(default=False)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Imagen"
        verbose_name_plural = "Imagenes"
        ordering = ['fecha_subida']

    def __str__(self):
        return f"Imagen de {self.usuario.email} subida el {self.fecha_subida.strftime('%Y-%m-%d')}"

    def save(self, *args, **kwargs):
        # Guardar primero para obtener el ID
        is_new = not self.pk
        super().save(*args, **kwargs)
        
        if is_new and self.imagen:
            # Renombrar con el ID real después de guardar
            self.rename_with_id()

    def rename_with_id(self):
        """Renombrar la imagen con el ID real de la base de datos"""
        try:
            old_path = self.imagen.path
            if os.path.exists(old_path):
                extension = self.imagen.name.split('.')[-1].lower()
                
                # Nuevo nombre: idusuario_imagen_idimagen
                new_filename = f"{self.usuario.usuario_id}_imagen_{self.id}.{extension}"
                new_path = os.path.join(os.path.dirname(old_path), new_filename)
                
                # Si ya existe un archivo con ese nombre, eliminarlo
                if os.path.exists(new_path):
                    os.remove(new_path)
                
                # Renombrar archivo físico
                os.rename(old_path, new_path)
                
                # Actualizar el campo en la base de datos sin llamar save() para evitar recursión
                Imagen.objects.filter(pk=self.pk).update(imagen=new_filename)
                
                # Actualizar la instancia actual
                self.imagen.name = new_filename
        except Exception as e:
            print(f"Error renombrando imagen: {e}")

    def delete(self, *args, **kwargs):
        """Eliminar el archivo físico junto con el registro"""
        if self.imagen and os.path.exists(self.imagen.path):
            os.remove(self.imagen.path)
        super().delete(*args, **kwargs)