from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from asgiref.sync import sync_to_async
from .models import VideoSession

@sync_to_async
def start_session(request):
    """Start a new video session."""
    new_session = VideoSession.objects.create(active=True)
    return Response({'session_id': str(new_session.session_id), 'message': 'Session started'}, status=status.HTTP_201_CREATED,content_type='application/json')

@sync_to_async
def end_session(request, session_id):
    """End an existing video session."""
    try:
        session = VideoSession.objects.get(session_id=session_id, active=True)
        session.active = False
        session.save()
        return Response({'message': 'Session ended successfully'}, status=status.HTTP_200_OK, content_type='application/json')
    
    except VideoSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND,content_type='application/json')

@sync_to_async
def active_sessions(request):
    """Retrieve all active video sessions."""
    sessions = list(VideoSession.objects.filter(active=True).values('session_id', 'start_time'))
    return Response({'sessions': sessions}, status=status.HTTP_200_OK, content_type='application/json')

@sync_to_async
def video_stream(req):
    return render(requesa=req, template_name='video_stream.html')