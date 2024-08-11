from rest_framework import serializers
from .models import Meal, MealPlan, DailyMeal

class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = ['id', 'category', 'meal', 'calories', 'carbohydrates', 'protein', 'fat']

class DailyMealSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyMeal
        fields = ['id', 'date', 'meals']

class MealPlanSerializer(serializers.ModelSerializer):
    daily_meals = DailyMealSerializer(many=True, read_only=True)

    class Meta:
        model = MealPlan
        fields = ['id', 'user', 'start_date', 'end_date', 'created_at', 'daily_meals']