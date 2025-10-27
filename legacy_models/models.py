from django.db import models
from django.contrib.auth.models import AbstractUser


class Genero(models.Model):
    genero_id = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=30)
    fecha_creacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        #managed = False
        db_table = 'genero'


class Orientacion(models.Model):
    orientacion_id = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=30)
    fecha_creacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        #managed = False
        db_table = 'orientacion'


class Programa(models.Model):
    programa_id = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=60)
    fecha_creacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        #managed = False
        db_table = 'programa'


class Semestresubicacion(models.Model):
    semestreubicacion_id = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50)

    class Meta:
        #managed = False
        db_table = 'semestresubicacion'


class Ubicacion(models.Model):
    ubicacion_id = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=100)
    fecha_creacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        #managed = False
        db_table = 'ubicacion'


class Usuario(AbstractUser):
    # Campos heredados de AbstractUser: username, first_name, last_name, email, password, etc.
    # Mapeamos los campos legacy a los de AbstractUser
    usuario_id = models.AutoField(primary_key=True)
    programa = models.ForeignKey(Programa, models.DO_NOTHING, blank=True, null=True)
    orientacion = models.ForeignKey(Orientacion, models.DO_NOTHING, blank=True, null=True)
    ubicacion = models.ForeignKey(Ubicacion, models.DO_NOTHING, blank=True, null=True)
    genero = models.ForeignKey(Genero, models.DO_NOTHING, blank=True, null=True)
    semestreubicacion = models.ForeignKey(Semestresubicacion, models.DO_NOTHING, blank=True, null=True)
    nombres = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=50)
    fechanacimiento = models.DateField()
    email = models.CharField(unique=True, max_length=60)  # Campo legacy, único
    contrasena = models.CharField(max_length=255)  # Este será mapeado a password
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

    # Mapeo de campos para compatibilidad con AbstractUser
    USERNAME_FIELD = 'email'  # Usar email como username
    REQUIRED_FIELDS = ['nombres', 'apellidos']  # Campos requeridos además del USERNAME_FIELD

    class Meta:
        #managed = False
        db_table = 'usuario'

    @property
    def first_name(self):
        return self.nombres

    @first_name.setter
    def first_name(self, value):
        self.nombres = value

    @property
    def last_name(self):
        return self.apellidos

    @last_name.setter
    def last_name(self, value):
        self.apellidos = value

    @property
    def password(self):
        return self.contrasena

    @password.setter
    def password(self, value):
        self.contrasena = value

    @property
    def id(self):
        return self.usuario_id

    def get_full_name(self):
        return f"{self.nombres} {self.apellidos}"

    def get_short_name(self):
        return self.nombres


class Verificacion(models.Model):
    verificacion_id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, models.DO_NOTHING, blank=True, null=True)
    codigo = models.CharField(max_length=50)
    fechacreacion = models.DateTimeField(blank=True, null=True)
    fechaexpiracion = models.DateTimeField()
    usado = models.BooleanField(blank=True, null=True)

    class Meta:
        #managed = False
        db_table = 'verificacion'
