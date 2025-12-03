# notificacion_app/utils.py

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def enviar_a_grupo(nombre_grupo: str, tipo_evento: str, data: dict):
    """
    Envía un evento a un grupo WebSocket usando Django Channels.
    
    :param nombre_grupo: nombre del grupo al que se enviará el mensaje.
    :param tipo_evento: corresponde al método que el consumer ejecutará.
    :param data: diccionario con los datos a enviar.
    """
    channel_layer = get_channel_layer()
    
    async_to_sync(channel_layer.group_send)(
        nombre_grupo,
        {
            "type": tipo_evento,  # Nombre del método en el consumer
            "data": data,
        }
    )
