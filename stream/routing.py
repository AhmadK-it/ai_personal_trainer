from django.urls import path
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from .consumers import VideoConsumer,VideoConsumerTestedEdition  

websocket_urlpatterns = [
    path('ws/video/stream/', VideoConsumer.as_asgi()), 
    path('ws/video/', VideoConsumerTestedEdition.as_asgi()), 
]

application = ProtocolTypeRouter({
    # Django's ASGI application to handle traditional HTTP requests
    "http": get_asgi_application(),

    # WebSocket chat handler
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
