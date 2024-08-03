from django.urls import path, re_path
from .consumers import VideoConsumerTestedEdition, VideoSessionConsumer, JSONSessionConsumer

websocket_urlpatterns = [
    path('ws/video/', VideoConsumerTestedEdition.as_asgi()), 
    path('ws/session/<uuid:session_id>/', VideoSessionConsumer.as_asgi()),
    path('ws/json_session/<uuid:session_id>/', JSONSessionConsumer.as_asgi()),
    #. re_path(r'ws/json_session/(?P<session_id>\w+)/$', JSONSessionConsumer.as_asgi()),

]
