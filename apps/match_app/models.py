# match_app/models.py
from django.db import models
from preferences_app.models import Preference
from django.conf import settings


class Perfil(models.Model):
    perfil_id = models.AutoField(primary_key=True)
    hobbies = models.TextField(null=True, blank=True)
    estatura = models.PositiveIntegerField(null=True, blank=True)
    estado = models.CharField(max_length=50, null=True, blank=True)
    likes = models.IntegerField(null=True, blank=True)
    fecharegistro = models.DateTimeField(null=True, blank=True)
    prefencias_id = models.IntegerField(null=True, blank=True)

    programa_academico_id = models.IntegerField(null=True, blank=True)
    ubicacion_id = models.IntegerField(null=True, blank=True)


    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        db_column="usuario_id",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "perfil"  

    def __str__(self):
        return f"Perfil #{self.perfil_id} (usuario_id={self.usuario_id})"

