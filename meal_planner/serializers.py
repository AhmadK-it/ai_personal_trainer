from rest_framework import serializers
from .models import Meal, MealPlan, DailyMeal, Recipe

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
        fields = ['id', 'start_date', 'end_date', 'created_at', 'daily_meals']

        
class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['name', 'ingredients', 'instructions']

class RecipeInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    nutrition_facts = serializers.JSONField()