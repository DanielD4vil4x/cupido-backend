import os

from django.core.asgi import get_asgi_application

#Necesario para Channels
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
#from channels.auth import AuthMiddlewareStack

from apps.chat_app.middleware import JwtAuthMiddleware
import apps.chat_app.routing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')


#application = get_asgi_application()

application = ProtocolTypeRouter({
    
    # Si el tráfico es HTTP, llama al "guardia HTTP" (la función original de Django)
    "http": get_asgi_application(), 

    # Si el tráfico es WebSocket, envíalo a la "oficina del chat"
    "websocket": AllowedHostsOriginValidator(
        
        JwtAuthMiddleware( # Esto averigua QUIÉN está chateando
            URLRouter(
                # Busca la dirección específica en tu app de chat
                apps.chat_app.routing.websocket_urlpatterns
            )
        )
    ),
})
#import os
#import django
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.security.websocket import AllowedHostsOriginValidator
#from django.core.asgi import get_asgi_application

# Si en el futuro usas autenticación por token o sesión
# from channels.auth import AuthMiddlewareStack

# Importa tus rutas WebSocket (cuando las tengas)
# from apps.chat_app.routing import websocket_urlpatterns

#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
#django.setup()

# ASGI application con soporte para HTTP y WebSocket
#application = ProtocolTypeRouter({
    # HTTP requests → Django normal
    #"http": get_asgi_application(),

    # WebSocket requests → (cuando los actives)
    # "websocket": AllowedHostsOriginValidator(
    #     AuthMiddlewareStack(
    #         URLRouter(websocket_urlpatterns)
    #     )
    # ),
#})

