from django.urls import path
from . import views

urlpatterns = [
    path('generate-meal-plan/', views.generate_meal_plan, name='generate_meal_plan'),
    path('view-meal-plan/<int:meal_plan_id>/', views.view_meal_plan, name='view_meal_plan'),
    path('view-daily-meal/<int:meal_plan_id>/<int:day>/', views.view_daily_meal, name='view_daily_meal'),
    path('update-meal-plan/', views.update_meal_plan, name='update_meal_plan'),
    path('update-generate-recipe/', views.generate_update_recipe, name='update_generate_recipe'),
    path('view-recipe/', views.view_recipe, name='view_recipe'),
]