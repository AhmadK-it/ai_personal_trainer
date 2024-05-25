from django.urls import path
from stream.consumers import VideoConsumer  # Replace with your actual consumer

websocket_urlpatterns = [
    path('ws/video/', VideoConsumer.as_asgi()),  # Replace with your actual path and consumer
]
