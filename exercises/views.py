from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import ExcerciseSerializer
from .models import Exercise


@api_view(['GET','OPTIONS'])
@permission_classes((IsAuthenticated, ))
def getExcercisesList(req):
    excercises = Exercise.objects.all()
    excercise_serializer = ExcerciseSerializer(excercises, many=True)
    data = {
        'excercises': excercise_serializer.data
    }
    return Response(data=data, status=status.HTTP_200_OK, content_type='application/json')


@api_view(['GET', 'OPTIONS'])
@permission_classes((IsAuthenticated, ))
def getExcercise(req, pk):  
    print(f'headers: {req.headers}')
    print(f'data: {req.data}')
    excercise = Exercise.objects.get(id=pk)
    excercise_serializer = ExcerciseSerializer(excercise, many=False)
    return Response(data=excercise_serializer.data, status=status.HTTP_200_OK, content_type='application/json')
    