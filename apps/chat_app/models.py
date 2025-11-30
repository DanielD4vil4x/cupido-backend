from django.db import models
from django.conf import settings # Para traer el modelo de Usuario
from apps.match_app.models import Match # Importamos el modelo de Match

# --- Este es el modelo para la SALA DE CHAT ---
# Corresponde a tu tabla "chat" en el diagrama.
# Requerimiento D-02: El chat solo existe si hay un match.
class Chat(models.Model):
    # Usamos OneToOneField para asegurar que un Match solo
    # puede tener UNA sala de chat. (FK_UNIQUE en tu diagrama).
    match = models.OneToOneField(
        Match,
        on_delete=models.CASCADE,
        related_name="chat"
    )
    
    # Requerimiento D-12: El chat se puede desactivar.
    activo = models.BooleanField(default=True)

    def __str__(self):
        # Esto es para que se vea bien en el panel de admin
        return f"Chat entre {self.match.usuarioA.nombres} y {self.match.usuarioB.nombres}"

# --- Este es el modelo para cada MENSAJE ---
# Corresponde a tu tabla "mensaje" en el diagrama.
class Mensaje(models.Model):
    # El chat al que pertenece este mensaje
    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name="mensajes",
        db_index=True # <--- OPTIMIZACIÓN
    )
    
    # El usuario que envió el mensaje
    remitente = models.ForeignKey(
        settings.AUTH_USER_MODEL, # Esta es la forma correcta de llamar a tu "Usuario"
        on_delete=models.SET_NULL, # Si se borra el usuario, el mensaje no se borra
        null=True,
        related_name="mensajes_enviados",
        db_index=True # <--- OPTIMIZACIÓN
    )
    
    # El contenido del mensaje
    contenido = models.TextField()
    
    # La fecha y hora. auto_now_add=True hace que se ponga la fecha automáticamente
    # cuando se crea el mensaje.
    fechaHora = models.DateTimeField(auto_now_add=True)

    # 🟢 CAMBIO PRINCIPAL: Campo para rastrear si el mensaje ha sido leído
    leido = models.BooleanField(default=False) # <--- ¡AÑADIDO!

    def __str__(self):
        return f"Mensaje de {self.remitente} en chat {self.chat.id}"

    class Meta:
        # Requerimiento D-04: Asegura que los mensajes siempre
        # se ordenen por fecha (el más viejo primero).
        ordering = ['fechaHora']