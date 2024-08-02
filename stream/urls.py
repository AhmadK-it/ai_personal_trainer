from django.urls import path
from . import views


urlpatterns = [
    path('video_stream/start/', views.video_stream, name='video_stream'),
    path('video_stream/list/', views.video_files, name='list_streams'),
    path('sessions/start/', views.start_session, name='start-session'),
    path('sessions/end/', views.end_session, name='end-session'),
    path('sessions/active/', views.active_sessions, name='active-sessions'),
    path('browse/', views.video_browser, name='video-browser'),
]
