from django.urls import path
from django.conf.urls import url
from . import views


urlpatterns = [
    path('video_stream/start/', views.video_stream, name='video_stream'),
    path('sessions/start/', views.start_session, name='start-session'),
    path('sessions/end/<uuid:session_id>/', views.end_session, name='end-session'),
    path('sessions/active/', views.active_sessions, name='active-sessions'),
]