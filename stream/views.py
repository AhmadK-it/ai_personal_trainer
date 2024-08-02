from django.shortcuts import render
from asgiref.sync import sync_to_async
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import VideoSession
from .serializers import DirectoryPathSerializer
from datetime import datetime
import os
from django.conf import settings
"""
y. the reasone why this request is critic and couldn't be removed is the user session must be created first
y. then connection for specific user session socket - in favor of async operation

"""
@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def start_session(req):
    new_session = VideoSession.objects.create(active=True)
    print({'session_id': str(new_session.session_id),
        'message': 'Session started'})
    return Response({
        'session_id': str(new_session.session_id),
        'message': 'Session started'
        }, status=status.HTTP_201_CREATED,
            content_type='application/json')


"""
r. TO BE DISCUSSED
y. could be remove since its job is being done from the socket disconnection
y. the reason is it true to be ignored since its job could be done without any further interaction from the client
y. it is enough to have the socket colsed to end the session

"""
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def end_session(req):
    try:
        session_id=req.data['session_id']
        session = VideoSession.objects.get(session_id=session_id, active=True)
        session.end_time = datetime.now()
        session.active = False
        session.save()
        return Response({'message': 'Session ended successfully'}, status=status.HTTP_200_OK, content_type='application/json')

    except VideoSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND,content_type='application/json')

#c Testing request
@api_view(['GET'])
def active_sessions(req):
    sessions = list(VideoSession.objects.filter(active=True).values('session_id', 'start_time'))
    return Response({'sessions': sessions}, status=status.HTTP_200_OK, content_type='application/json')

#c Testing request
def video_stream(req):
    return render(request=req, template_name='video_stream.html')


@api_view(['GET'])
def video_files(request):
    video_path = os.path.join('server', 'static', 'videos')
    
    if not os.path.exists(video_path):
        return Response({"error": "Video directory does not exist"}, status=status.HTTP_404_NOT_FOUND)
    
    video_files = []
    for filename in os.listdir(video_path):
        if filename.endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):  # Add or remove video extensions as needed
            file_path = os.path.join(video_path, filename)
            file_stats = os.stat(file_path)
            video_files.append({
                "name": filename,
                "size": file_stats.st_size,
                "created_at": file_stats.st_ctime,
                "modified_at": file_stats.st_mtime
            })
    
    return Response({"videos": video_files})

def video_browser(request):
    video_path = os.path.join('server', 'static', 'videos')
    videos = []
    
    if os.path.exists(video_path):
        for filename in os.listdir(video_path):
            if filename.endswith(('.mp4', '.avi', '.mov', '.mkv','.webm')):
                videos.append(filename)
    
    return render(request, 'video_browser.html', {'videos': videos})
