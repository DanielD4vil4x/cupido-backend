from django.db import models
from django.contrib.postgres.fields import JSONField
from apps.auth_app.models import Usuario, Programa, Ubicacion

class Perfil(models.Model):
    perfil_id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, models.DO_NOTHING)
    programa_academico = models.ForeignKey(Programa, models.DO_NOTHING, blank=True, null=True)
    ubicacion = models.ForeignKey(Ubicacion, models.DO_NOTHING, blank=True, null=True)
    hobbies = JSONField(blank=True, null=True)
    estatura = models.FloatField(blank=True, null=True)
    estado = models.CharField(max_length=50, blank=True, null=True)
    likes = models.IntegerField(blank=True, null=True)
    fecharegistro = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Perfil de {self.usuario}" if self.usuario else "Perfil sin usuario"

    class Meta:
        db_table = 'perfil'
        managed = False
