from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from .models import User, UserProfile

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=255, min_length=6, write_only=True)
    
    class Meta:
        model=User
        fields=("username","email","password")
        
    def create(self, validate_data):
        user=User.objects.create_user(
            username=validate_data.get("username"), 
            email=validate_data.get("email"), 
            password=validate_data.get("password")
        )
        return user

class UserLoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255, min_length=5, write_only=True)
    # email = serializers.EmailField(max_length=255, min_length=6)
    access_token = serializers.CharField(max_length=255, min_length=6, read_only=True)
    refresh_token = serializers.CharField(max_length=255, min_length=6, read_only=True)
    
    class Meta:
        model=User
        fields=('username', 'password', 'access_token', 'refresh_token')

    def validate(self, attrs):
        user=authenticate(
            request=self.context.get('request'), 
            username=attrs.get('username'),
            password=attrs.get('password')
            )
        
        if not user:
            print(self.context.get('request'))
            raise AuthenticationFailed('invalid credentials try again ')
        
        tokens=user.get_tokens()
        
        return {
            'username': user.username,
            'access_token': str(tokens.get('access')),
            'refresh_token': str(tokens.get('refresh')),
        }

class UserLogoutSerializer(serializers.Serializer):
    refresh=serializers.CharField()
    
    default_error_messages={
        'bad_token' : ('token is not valid or expired')
    }
    
    def validate(self, attrs):
        self.token= attrs.get('refresh')
        return attrs
    
    def save(self, **kwargs):
        try:
            token=RefreshToken(self.token)
            token.blacklist()
        except TokenError:
            return self.fail('bad_token')

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['age', 'gender', 'weight', 'height', 'body_fat', 'goal', 'lifestyle_intensity', 'recommended_calories', 'weakness_points', 'experience_level']

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['age', 'gender', 'weight', 'height', 'body_fat', 'goal', 'lifestyle_intensity', 'recommended_calories', 'weakness_points', 'experience_level']