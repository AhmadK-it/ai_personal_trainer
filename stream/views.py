from django.shortcuts import render
from asgiref.sync import sync_to_async
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import VideoSession
from datetime import datetime

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