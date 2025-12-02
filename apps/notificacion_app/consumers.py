import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        user = self.scope["user"]

        # 1. Tomar user_id desde la URL
        url_user_id = self.scope["url_route"]["kwargs"].get("user_id")

        # 2. Validar autenticación
        if user.is_anonymous:
            await self.close()
            return
        
        # 3. Validar que el user_id de la URL coincide con el user.id autenticado
        try:
            url_user_id = int(url_user_id)
        except (ValueError, TypeError):
            await self.close()
            return

        if user.id != url_user_id:
            # Usuario intentando conectarse con el ID de otro → rechazar
            await self.close()
            return

        # 4. Asignar nombre de grupo seguro
        self.group_name = f"user_{user.id}"

        # 5. Unirse al grupo
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        # 6. Conexión aceptada
        await self.accept()


    async def disconnect(self, close_code):
        """Remover del grupo al desconectar"""
        await self.channel_layer.group_discard(self.group_name, self.channel_name)


    async def notification_message(self, event):
        """Enviar el mensaje recibido desde group_send al cliente WebSocket"""
        await self.send(text_data=json.dumps(event["data"]))
