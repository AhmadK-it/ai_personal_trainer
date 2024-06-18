from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import UserLoginSerializer, UserRegisterSerializer, UserLogoutSerializer

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
                }, status=status.HTTP_400_BAD_REQUEST)

class LoginUserView(GenericAPIView):
    serializer_class=UserLoginSerializer
    def post(self,req):
        serializer=self.serializer_class(data=req.data, context={'request': req})
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