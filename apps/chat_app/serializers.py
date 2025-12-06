from rest_framework import serializers
from .models import Chat, Mensaje
from django.contrib.auth import get_user_model

# Importar modelos y servicios para imágenes
from apps.profile_app.subapps.imageUpload.models import Imagen
from apps.profile_app.subapps.imageUpload.services import generate_presigned_url

# Obtenemos el modelo de usuario personalizado de Django
User = get_user_model()

# -----------------------------------------------
# 1. Serializador Básico para el Contacto
# Se usa para representar a la 'otra persona' del chat.
# Incluye imagen_principal para mostrar en la lista de chats.
# -----------------------------------------------
class ContactoChatSerializer(serializers.ModelSerializer):
    imagen_principal = serializers.SerializerMethodField()

    class Meta:
        model = User
        # Adapta estos campos a los que quieres mostrar en el panel de lista de chats
        # last_login viene de AbstractUser y lo usaremos como "última vez en línea"
        fields = ('id', 'nombres', 'apellidos', 'email', 'last_login', 'imagen_principal')

    def get_imagen_principal(self, obj):
        """Obtiene URL presignada de la imagen principal del contacto."""
        try:
            # Buscar imagen principal primero
            imagen = Imagen.objects.filter(
                usuario_id=obj.id, 
                es_principal=True
            ).first()
            # Si no hay imagen principal, buscar cualquier imagen
            if not imagen:
                imagen = Imagen.objects.filter(usuario_id=obj.id).first()
            # Generar presigned URL si existe imagen
            if imagen and imagen.imagen:
                return generate_presigned_url(imagen.imagen.name, expiration=3600)
        except Exception:
            pass
        return None 

# -----------------------------------------------
# 2. Serializador del Último Mensaje
# Solo necesitamos el contenido y la fecha/hora para la lista de chats.
# -----------------------------------------------
class UltimoMensajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mensaje
        fields = ('contenido', 'fechaHora')

# -----------------------------------------------
# 3. Serializador Principal de la Lista de Chats (El Reto)
# Utiliza campos de métodos y campos anotados para ser eficiente.
# -----------------------------------------------
class ChatListSerializer(serializers.ModelSerializer):
    # 🟢 CAMPO 1: El objeto del último mensaje. 
    # El 'source' se mapeará al campo anotado que crearemos en la vista (latest_message_data).
    ultimo_mensaje = UltimoMensajeSerializer(source='latest_message_data', read_only=True)
    
    # 🟢 CAMPO 2: El conteo de mensajes no leídos.
    # Se mapeará al campo anotado que crearemos en la vista (no_leidos).
    no_leidos = serializers.IntegerField(read_only=True)
    
    # 🟢 CAMPO 3: Identifica a la otra persona en el chat (requiere lógica).
    contacto = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        # Note que no incluimos 'match' ya que usamos el campo 'contacto'
        fields = ('id', 'activo', 'contacto', 'ultimo_mensaje', 'no_leidos')

    def get_contacto(self, obj):
        """
        Determina cuál de los dos usuarios en el Match es el 'contacto' (el opuesto al usuario actual).
        """
        # Necesitamos el usuario que hizo la solicitud (el usuario loggeado)
        request = self.context.get('request')
        if not request:
            # Esto nunca debería pasar en una vista autenticada
            return None 

        user = request.user
        match = obj.match
        
        # Lógica para determinar el contacto opuesto
        if match.usuarioA == user:
            contacto = match.usuarioB
        else:
            contacto = match.usuarioA
            
        # Serializamos y devolvemos la data del contacto
        return ContactoChatSerializer(contacto).data