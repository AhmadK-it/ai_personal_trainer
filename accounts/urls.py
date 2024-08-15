from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from . import views


urlpatterns=[
    path('register/', views.RegisterUserView.as_view(), name='register'),
    path('login/', views.loginView, name='login'),
    path('logout/', views.LogoutUserView.as_view(), name='logout'),
    path('test/', views.TestAuthView.as_view(), name='test-auth'),
    path('token/refresh/', TokenRefreshView.as_view(), name='new_refresh_token'),
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/update/', views.update_user_profile, name='update_user_profile'),
]

