from django.utils import timezone
from apps.perfil.models import Perfil
from apps.auth_app.models import Usuario, Programa, Ubicacion

class PerfilUtils:
    @staticmethod
    def create_perfil(data):
        """
        Crea un perfil validando las relaciones y asignando valores por defecto.
        """
        usuario_id = data.get('usuario')
        programa_id = data.get('programa_academico')
        ubicacion_id = data.get('ubicacion')
        hobbies = data.get('hobbies', {})
        estatura = data.get('estatura')
        estado = data.get('estado') or "Encupidado"
        likes = data.get('likes') or 0

        # Validaciones de relaciones
        try:
            usuario = Usuario.objects.get(pk=usuario_id)
        except Usuario.DoesNotExist:
            raise ValueError("El usuario especificado no existe")

        programa = None
        if programa_id:
            try:
                programa = Programa.objects.get(pk=programa_id)
            except Programa.DoesNotExist:
                raise ValueError("El programa académico especificado no existe")

        ubicacion = None
        if ubicacion_id:
            try:
                ubicacion = Ubicacion.objects.get(pk=ubicacion_id)
            except Ubicacion.DoesNotExist:
                raise ValueError("La ubicación especificada no existe")

        # Creación del perfil con valores por defecto gestionados aquí
        perfil = Perfil.objects.create(
            usuario=usuario,
            programa_academico=programa,
            ubicacion=ubicacion,
            hobbies=hobbies,
            estatura=estatura,
            estado=estado,
            likes=likes,
            fecharegistro=timezone.now()
        )

        return perfil
