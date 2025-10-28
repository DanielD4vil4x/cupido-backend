# apps/auth_app/serializers/user_get_serializer.py

from rest_framework import serializers
from legacy_models.models import Usuario


class UserGetSerializer(serializers.Serializer):
    """
    Serializa todos los campos del perfil de usuario para respuestas GET.
    Este serializer es de solo lectura y devuelve toda la información del usuario autenticado.
    """
    
    usuario_id = serializers.IntegerField()
    nombres = serializers.CharField()
    apellidos = serializers.CharField()
    email = serializers.EmailField()
    fechanacimiento = serializers.DateField()
    apodo = serializers.CharField()
    numerotelefono = serializers.CharField()
    imagen_principal = serializers.CharField(allow_null=True)
    descripcion = serializers.CharField(allow_null=True, allow_blank=True)
    gustos = serializers.CharField(allow_null=True, allow_blank=True)
    estatura = serializers.FloatField(allow_null=True)
    likes = serializers.IntegerField(allow_null=True)
    filtros = serializers.CharField(allow_null=True, allow_blank=True)
    fecharegistro = serializers.DateTimeField(allow_null=True)
    estadocuenta = serializers.CharField(allow_null=True, allow_blank=True)
    tyc = serializers.BooleanField(allow_null=True)
    
    # Foreign key relations
    programa_id = serializers.IntegerField(allow_null=True, source='programa.programa_id')
    orientacion_id = serializers.IntegerField(allow_null=True, source='orientacion.orientacion_id')
    ubicacion_id = serializers.IntegerField(allow_null=True, source='ubicacion.ubicacion_id')
    genero_id = serializers.IntegerField(allow_null=True, source='genero.genero_id')
    genero_descripcion = serializers.CharField(allow_null=True, source='genero.descripcion')
    semestreubicacion_id = serializers.IntegerField(allow_null=True, source='semestreubicacion.semestreubicacion_id')


def serialize_user_profile(user: Usuario) -> dict:
    """
    Serializa todos los campos del usuario en un diccionario.
    Maneja las relaciones FK de forma segura.
    """
    return {
        "usuario_id": user.usuario_id,
        "nombres": user.nombres,
        "apellidos": user.apellidos,
        "email": user.email,
        "fechanacimiento": user.fechanacimiento,
        "apodo": user.apodo,
        "numerotelefono": user.numerotelefono,
        "imagen_principal": user.imagen_principal,
        "descripcion": user.descripcion,
        "gustos": user.gustos,
        "estatura": user.estatura,
        "likes": user.likes,
        "filtros": user.filtros,
        "fecharegistro": user.fecharegistro,
        "estadocuenta": user.estadocuenta,
        "tyc": user.tyc,
        "genero_id": user.genero.genero_id if user.genero else None,
        "genero_descripcion": user.genero.descripcion if user.genero else None,
        "programa_id": user.programa.programa_id if user.programa else None,
        "orientacion_id": user.orientacion.orientacion_id if user.orientacion else None,
        "ubicacion_id": user.ubicacion.ubicacion_id if user.ubicacion else None,
        "semestreubicacion_id": user.semestreubicacion.semestreubicacion_id if user.semestreubicacion else None,
    }

