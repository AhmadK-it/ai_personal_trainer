from django.urls import path
from .consumers import VideoConsumerTestedEdition, VideoSessionConsumer

websocket_urlpatterns = [
    path('ws/video/', VideoConsumerTestedEdition.as_asgi()), 
    path('ws/session/<uuid:session_id>/', VideoSessionConsumer.as_asgi()),
]
