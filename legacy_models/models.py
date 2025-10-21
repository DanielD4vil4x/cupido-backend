from django.db import models


class Genero(models.Model):
    genero_id = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=30)
    fecha_creacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'genero'


class Orientacion(models.Model):
    orientacion_id = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=30)
    fecha_creacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'orientacion'


class Programa(models.Model):
    programa_id = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=60)
    fecha_creacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'programa'


class Semestresubicacion(models.Model):
    semestreubicacion_id = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'semestresubicacion'


class Ubicacion(models.Model):
    ubicacion_id = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=100)
    fecha_creacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ubicacion'


class Usuario(models.Model):
    usuario_id = models.AutoField(primary_key=True)
    programa = models.ForeignKey(Programa, models.DO_NOTHING, blank=True, null=True)
    orientacion = models.ForeignKey(Orientacion, models.DO_NOTHING, blank=True, null=True)
    ubicacion = models.ForeignKey(Ubicacion, models.DO_NOTHING, blank=True, null=True)
    genero = models.ForeignKey(Genero, models.DO_NOTHING, blank=True, null=True)
    semestreubicacion = models.ForeignKey(Semestresubicacion, models.DO_NOTHING, blank=True, null=True)
    nombres = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=50)
    fechanacimiento = models.DateField()
    email = models.CharField(unique=True, max_length=60)
    contrasena = models.CharField(max_length=255)
    apodo = models.CharField(max_length=50)
    numerotelefono = models.CharField(max_length=15)
    imagen_principal = models.CharField(max_length=255, blank=True, null=True)
    descripcion = models.CharField(max_length=500, blank=True, null=True)
    gustos = models.CharField(max_length=255, blank=True, null=True)
    estatura = models.FloatField(blank=True, null=True)
    likes = models.IntegerField(blank=True, null=True)
    filtros = models.CharField(max_length=255, blank=True, null=True)
    fecharegistro = models.DateTimeField(blank=True, null=True)
    estadocuenta = models.CharField(max_length=50, blank=True, null=True)
    tyc = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usuario'


class Verificacion(models.Model):
    verificacion_id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, models.DO_NOTHING, blank=True, null=True)
    codigo = models.CharField(max_length=50)
    fechacreacion = models.DateTimeField(blank=True, null=True)
    fechaexpiracion = models.DateTimeField()
    usado = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'verificacion'
