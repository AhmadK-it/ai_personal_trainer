from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from . import views


urlpatterns=[
    path('register/', views.RegisterUserView.as_view(), name='register'),
    path('login/', views.LoginUserView.as_view(), name='login'),
    path('logout/', views.LogoutUserView.as_view(), name='logout'),
    path('test/', views.TestAuthView.as_view(), name='test-auth'),
    path('token/refresh/', TokenRefreshView.as_view(), name='new_refresh_token'),
]

