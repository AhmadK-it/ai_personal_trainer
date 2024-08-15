from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import UserProfile
from .serializers import UserLoginSerializer, UserRegisterSerializer, UserLogoutSerializer, UserProfileSerializer, UserProfileUpdateSerializer

class RegisterUserView(GenericAPIView):
    serializer_class=UserRegisterSerializer
    
    def post(self, req):
            user_data=req.data
            serializer=self.serializer_class(data=user_data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                user=serializer.data
                return Response({
                    'msg':'msg is good',
                    'data': user,
                    'content-type': f'{req.content_type}'
                }, status=status.HTTP_201_CREATED, content_type='application/json')
            else:
                return Response({
                    'msg': f'{serializer.errors}',
                    'data': f'{req.data}'
                }, status=status.HTTP_400_BAD_REQUEST,  content_type='application/json')

class LoginUserView(GenericAPIView):
    serializer_class=UserLoginSerializer
    def post(self,req):
        print(f'req obj: {req}')
        print(f'headers: {req.headers}')
        print(f'data: {req.data}')
        # return Response({}, status=status.HTTP_200_OK)
        serializer=self.serializer_class(data=req.data, context={'request': req})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK, content_type='application/json')

@api_view(['POST', 'OPTIONS'])
def loginView(req):
        serializer_class=UserLoginSerializer
        print(f'req obj: {req}')
        print(f'headers: {req.headers}')
        print(f'data: {req.data}')
        # return Response({}, status=status.HTTP_200_OK)
        serializer=serializer_class(data=req.data, context={'request': req})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK, content_type='application/json')
    

class LogoutUserView(GenericAPIView):
    serializer_class=UserLogoutSerializer
    permission_classes=[IsAuthenticated]
    def post(self,req):
        serializer=self.serializer_class(data=req.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT, content_type='application/json')
    

class TestAuthView(GenericAPIView):
    permission_classes=[IsAuthenticated]
    def get(self, req):
        data={
            'msg': 'all set'
        }
        return Response(data, status=status.HTTP_200_OK, content_type='application/json')


@api_view(['GET', 'POST', 'OPTIONS'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def user_profile(request):
    if request.method == 'OPTIONS':
        response = HttpResponse()
        response['Allow'] = 'GET, POST, OPTIONS'
        response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = None
    print(request.method)
    if request.method == 'GET':
        if profile:
            serializer = UserProfileSerializer(profile)
            return Response({
                'msg': "User's profile found:",
                'data':serializer.data
                }, 
                            status=status.HTTP_200_OK, 
                            content_type='application/json')
        return Response({"msg": "Profile not found"}, status=status.HTTP_400_BAD_REQUEST,  content_type='application/json')

    elif request.method == 'POST':
        if profile:
            return Response({"msg": "Profile already exists"}, status=status.HTTP_400_BAD_REQUEST,  content_type='application/json')
        
        serializer = UserProfileUpdateSerializer(data=request.data.get('profile',{}))
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED , content_type='application/json')
        return Response({
                    'msg': f'{serializer.errors}',
                    'data': f'{request.data}'
                }, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return Response({"msg": "Profile not found"}, status=status.HTTP_404_NOT_FOUND,  content_type='application/json')

    serializer = UserProfileUpdateSerializer(profile, data=request.data.get('profile',{}), partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
                'msg': "User's profile updated:",
                'data':serializer.data
                }, 
                            status=status.HTTP_200_OK, 
                            content_type='application/json')
    return Response({
                    'msg': f'{serializer.errors}',
                    'data': f'{request.data}'
                }, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')