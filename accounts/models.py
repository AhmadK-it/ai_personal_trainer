from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
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
    
    WEAKNESS_CHOICES = [
        'No',
        'Shoulder',
        'Knee',
        'Hips',
        'Lower Back',
        'Elbow',
        'Wrist',
        'Ankle',
        'Neck',
    ]
    EXPERIENCE_CHOICES = [
        ('BEGINNER', 'Beginner'),
        ('INTERMEDIATE_ADVANCED', 'Intermediate & Advanced'),
    ]

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    GOAL_CHOICES = [
        ('weight_loss', 'Weight Loss'),
        ('weight_gain', 'Weight Gain'),
        ('muscle_gain', 'Muscle Gain'),
    ]

    LIFESTYLE_CHOICES = [
        ('sedentary', 'Sedentary'),
        ('moderate', 'Moderate'),
        ('intensive', 'Intensive'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)  # in kg
    height = models.FloatField(null=True, blank=True)  # in cm
    body_fat = models.FloatField(null=True, blank=True)  # in percentage
    goal = models.CharField(max_length=20, choices=GOAL_CHOICES, null=True, blank=True)
    lifestyle_intensity = models.CharField(max_length=20, choices=LIFESTYLE_CHOICES, null=True, blank=True)
    recommended_calories = models.FloatField(null=True, blank=True)
    weakness_points = models.CharField(max_length=255, blank=True, null=True)
    experience_level = models.CharField(max_length=50, choices=EXPERIENCE_CHOICES, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def set_weakness_points(self, points):
        if points and len(points) > 2:
            raise ValidationError("You can select up to 3 weakness points.")
        self.weakness_points = ','.join(points) if points else None

    def get_weakness_points(self):
        return self.weakness_points.split(',') if self.weakness_points else []

    def update_basic_info(self, age, weight, height, weakness_points, experience_level):
        self.age = age
        self.weight = weight
        self.height = height
        self.set_weakness_points(weakness_points)
        self.experience_level = experience_level
        self.full_clean()
        self.save()

    def update_detailed_info(self, age, weight, height, gender, body_fat, goal, lifestyle_intensity, recommended_calories):
        self.age = age
        self.weight = weight
        self.height = height
        self.gender = gender
        self.body_fat = body_fat
        self.goal = goal
        self.lifestyle_intensity = lifestyle_intensity
        self.recommended_calories = recommended_calories
        self.full_clean()
        self.save()

    def clean(self):
        super().clean()
        weakness_points = self.get_weakness_points()
        if weakness_points and len(weakness_points) > 2:
            raise ValidationError("You can select up to 3 weakness points.")
        for point in weakness_points:
            if point not in self.WEAKNESS_CHOICES:
                raise ValidationError(f"{point} is not a valid weakness point.")