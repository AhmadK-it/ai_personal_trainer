from django.urls import path, include
from . import views


urlpatterns=[
    path('list/', views.getExcercisesList, name='exercises_list'),
    path('exercise/<str:pk>/', views.getExcercise, name='exercise'),
]

