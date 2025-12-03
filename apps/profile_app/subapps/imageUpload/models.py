from django.db import models
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from apps.auth_app.models import Usuario
import os
import uuid
from django.conf import settings

def user_directory_path(instance, filename):
    """
    Genera ruta de almacenamiento organizada por usuario.
    Lógica: Los archivos se guardan en carpetas por usuario para mejor organización
    en MinIO/S3. Formato: imagenes/usuarios/{usuario_id}/temp_{uuid}.{ext}
    
    NOTA: El bucket en producción es 'multimediacupido' y ya tiene la carpeta 'imagenes/',
    por lo que usamos esa estructura base para mantener consistencia.
    """
    extension = filename.split('.')[-1].lower()
    # Nombre temporal con UUID - se renombrará después con el ID real
    temp_name = f"temp_{uuid.uuid4().hex[:8]}.{extension}"
    # Organizar por carpeta de usuario dentro de imagenes/
    return f"imagenes/usuarios/{instance.usuario.usuario_id}/{temp_name}"

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
        
        # Asegurar que solo exista una imagen principal por usuario
        if self.es_principal:
            # Desmarcar otras imágenes principales del mismo usuario
            Imagen.objects.filter(usuario=self.usuario).exclude(pk=self.pk).update(es_principal=False)

        if is_new and self.imagen:
            # Renombrar con el ID real después de guardar (usa default_storage para compatibilidad)
            self.rename_with_id()

    def rename_with_id(self):
        """
        Renombrar la imagen con el ID real de la base de datos.
        Lógica: Después de guardar, renombramos el archivo temporal para usar
        un nombre definitivo basado en el ID del usuario y la imagen.
        Formato final: usuarios/{usuario_id}/{usuario_id}_imagen_{imagen_id}.{ext}
        """
        try:
            # Utilizar default_storage para soportar backends remotos (S3/MinIO)
            storage = default_storage
            current_name = self.imagen.name
            if not current_name:
                return

            extension = current_name.split('.')[-1].lower()
            new_filename = f"{self.usuario.usuario_id}_imagen_{self.id}.{extension}"
            
            # Mantener la estructura de carpetas: imagenes/usuarios/{usuario_id}/
            dir_name = os.path.dirname(current_name)
            if dir_name:
                new_name = os.path.join(dir_name, new_filename)
            else:
                new_name = f"imagenes/usuarios/{self.usuario.usuario_id}/{new_filename}"

            # Abrir archivo actual y guardar con nuevo nombre
            with self.imagen.open('rb') as f:
                content = ContentFile(f.read())
                saved_name = storage.save(new_name, content)

            # Borrar el archivo temporal si existe y es diferente
            if storage.exists(current_name) and current_name != saved_name:
                try:
                    storage.delete(current_name)
                except Exception:
                    # No bloquear la operación principal si la eliminación falla
                    pass

            # Actualizar DB y la instancia local
            Imagen.objects.filter(pk=self.pk).update(imagen=saved_name)
            self.imagen.name = saved_name
        except Exception as e:
            # En producción usar logger; aquí mostramos el error para debug
            print(f"Error renombrando imagen: {e}")

    def delete(self, *args, **kwargs):
        """Eliminar el archivo físico junto con el registro"""
        if self.imagen and self.imagen.name:
            try:
                default_storage.delete(self.imagen.name)
            except Exception:
                # Si falla la eliminación física, no bloquear la eliminación del registro
                pass
        super().delete(*args, **kwargs)