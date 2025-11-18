import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_asgi_application()

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

