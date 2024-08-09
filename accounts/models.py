from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken
from .managers import MyUserManager


class User(AbstractBaseUser, PermissionsMixin):
    username=models.CharField(max_length=255, unique=True,verbose_name=_('user name'))
    email= models.EmailField(max_length=255, unique=True, verbose_name=_('email address'))
    is_staff=models.BooleanField(default=False)
    is_superuser=models.BooleanField(default=False)
    is_verified=models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)
    date_joined=models.DateTimeField(auto_now_add=True)
    last_login=models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD="username"
    
    
    REQUIRED_FIELDS=["email"]
    
    objects= MyUserManager()
    
    def __str__(self):
        return self.username
    
    def get_tokens(self):
        refresh = RefreshToken.for_user(self)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female')])
    weight = models.FloatField()  # in kg
    height = models.FloatField()  # in cm
    body_fat = models.FloatField()  # in percentage
    goal = models.CharField(max_length=20, choices=[
        ('weight_loss', 'Weight Loss'),
        ('weight_gain', 'Weight Gain'),
        ('muscle_gain', 'Muscle Gain')
    ])
    lifestyle_intensity = models.CharField(max_length=20, choices=[
        ('sedentary', 'Sedentary'),
        ('moderate', 'Moderate'),
        ('intensive', 'Intensive')
    ])
    recommended_calories = models.FloatField(default=0)

    def __str__(self):
        return f"{self.user.username}'s Profile"