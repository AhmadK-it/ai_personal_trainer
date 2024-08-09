from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from accounts.models import UserProfile
from django.shortcuts import get_object_or_404
from .models import Meal, MealPlan, DailyMeal
from django.db.models import Q
import random
from datetime import date, timedelta


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def generate_meal_plan(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return Response({"detail": "User profile not found"}, status=404)

    expert_system = ExpertSystem(profile)
    weekly_meal_plan = expert_system.get_weekly_meal_plan()

    start_date = date.today()
    end_date = start_date + timedelta(days=6)

    meal_plan = MealPlan.objects.create(
        user=request.user,
        start_date=start_date,
        end_date=end_date
    )

    for i, daily_meals in enumerate(weekly_meal_plan):
        DailyMeal.objects.create(
            meal_plan=meal_plan,
            date=start_date + timedelta(days=i),
            meals=daily_meals
        )

    return Response({"message": "Meal plan generated successfully", "meal_plan_id": meal_plan.id})

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def view_meal_plan(request, meal_plan_id):
    meal_plan = get_object_or_404(MealPlan, id=meal_plan_id, user=request.user)
    daily_meals = meal_plan.daily_meals.all().order_by('date')

    plan_data = {
        "start_date": meal_plan.start_date,
        "end_date": meal_plan.end_date,
        "daily_meals": [
            {
                "date": daily_meal.date,
                "meals": daily_meal.meals
            } for daily_meal in daily_meals
        ]
    }

    return Response(plan_data)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def view_daily_meal(request, meal_plan_id, day):
    meal_plan = get_object_or_404(MealPlan, id=meal_plan_id, user=request.user)
    target_date = meal_plan.start_date + timedelta(days=day-1)
    daily_meal = get_object_or_404(DailyMeal, meal_plan=meal_plan, date=target_date)

    return Response({
        "date": daily_meal.date,
        "meals": daily_meal.meals
    })

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_meal_plan(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return Response({"detail": "User profile not found"}, status=404)

    # Delete the old meal plan
    MealPlan.objects.filter(user=request.user).delete()

    # Generate a new meal plan
    expert_system = ExpertSystem(profile)
    weekly_meal_plan = expert_system.get_weekly_meal_plan()

    start_date = date.today()
    end_date = start_date + timedelta(days=6)

    meal_plan = MealPlan.objects.create(
        user=request.user,
        start_date=start_date,
        end_date=end_date
    )

    for i, daily_meals in enumerate(weekly_meal_plan):
        DailyMeal.objects.create(
            meal_plan=meal_plan,
            date=start_date + timedelta(days=i),
            meals=daily_meals
        )

    return Response({"message": "Meal plan updated successfully", "meal_plan_id": meal_plan.id})


class ExpertSystem:
    def __init__(self, user_profile):
        self.user = user_profile
        self.calculate_bmr()
        self.calculate_recommended_calories()
        self.adjust_calories_based_on_lifestyle()
        self.adjust_calories_based_on_goal()

    # Implement the methods from the original ExpertSystem class here

    def get_daily_meal_plan(self):
        # Define meal counts based on calorie needs
        if self.user.recommended_calories >= 3500:
            meal_counts = {'breakfast': 2, 'lunch': 2, 'dinner': 1, 'snacks': 3}
        elif 3000 <= self.user.recommended_calories < 3500:
            meal_counts = {'breakfast': 1, 'lunch': 2, 'dinner': 1, 'snacks': 3}
        else:
            meal_counts = {'breakfast': 1, 'lunch': 1, 'dinner': 1, 'snacks': 3}

        selected_meals = []

        for meal_type, count in meal_counts.items():
            meals_of_type = list(Meal.objects.filter(category=meal_type))
            selected_meals.extend(random.sample(meals_of_type, count))

        # Adjust meal portions to meet the required calories
        total_calories = sum(meal.calories for meal in selected_meals)
        total_protein = sum(meal.protein for meal in selected_meals)
        total_fat = sum(meal.fat for meal in selected_meals)

        scaling_factor = self.user.recommended_calories / total_calories
        protein_scaling_factor = self.user.weight * self.user.protein_multiplier / total_protein
        fat_scaling_factor = self.user.weight * self.user.fat_multiplier / total_fat

        adjusted_meals = []
        for meal in selected_meals:
            adjusted_meal = {
                'category': meal.category,
                'meal': meal.meal,
                'calories': meal.calories * scaling_factor,
                'protein': meal.protein * protein_scaling_factor,
                'fat': meal.fat * fat_scaling_factor,
            }
            adjusted_meal['carbohydrates'] = (adjusted_meal['calories'] - (adjusted_meal['protein'] * 4 + adjusted_meal['fat'] * 9)) / 4
            adjusted_meals.append(adjusted_meal)

        return adjusted_meals
    
    def get_weekly_meal_plan(self):
        return [self.get_daily_meal_plan() for _ in range(7)]
    