from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from accounts.models import UserProfile
from django.shortcuts import get_object_or_404
from .models import MealPlan, DailyMeal, Recipe
import random
from datetime import date, timedelta
from .expert_system import NutritionExpertSystem, User
from experta import Fact
from .serializers import MealPlanSerializer, MealSerializer, DailyMealSerializer, RecipeInputSerializer, RecipeSerializer
from .cohere_recipe import generate_recipe
import json
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def generate_meal_plan(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    # Update user profile with the data from the request
    profile_data = request.data.get('profile', {})
    profile.update_detailed_info(
        age=profile_data.get('age', profile.age),
        weight=profile_data.get('weight', profile.weight),
        height=profile_data.get('height', profile.height),
        gender=profile_data.get('gender', profile.gender),
        body_fat=profile_data.get('body_fat', profile.body_fat),
        goal=profile_data.get('goal', profile.goal),
        lifestyle_intensity=profile_data.get('lifestyle_intensity', profile.lifestyle_intensity),
        recommended_calories=profile_data.get('recommended_calories', profile.recommended_calories)
    )
    # Initialize and run the expert system
    expert_system = NutritionExpertSystem()
    expert_system.reset()
    expert_system.declare(User(
        age=profile.age,
        gender=profile.gender,
        weight=profile.weight,
        height=profile.height,
        body_fat=profile.body_fat,
        goal=profile.goal,
        lifestyle_intensity=profile.lifestyle_intensity,
        recommended_calories=profile.recommended_calories
    ))
    expert_system.run()

    # Extract the weekly meal plan from the expert system
  # Extract the weekly meal plan from the expert system
    weekly_plan = expert_system.weekly_plan if hasattr(expert_system, 'weekly_plan') else None

    if not weekly_plan:
        return Response({"detail": "Failed to generate meal plan"}, status= status.HTTP_400_BAD_REQUEST, content_type='application/json')

    # Create MealPlan and DailyMeal objects
    start_date = date.today()
    end_date = start_date + timedelta(days=6)

    meal_plan = MealPlan.objects.create(
        user=request.user,
        start_date=start_date,
        end_date=end_date
    )

    for i, daily_meals in enumerate(weekly_plan):
        DailyMeal.objects.create(
            meal_plan=meal_plan,
            date=start_date + timedelta(days=i),
            meals=daily_meals
        )

    # Prepare the response data
    response_data = {
        "message": "Meal plan generated successfully",
        "meal_plan_id": meal_plan.id,
        "start_date": start_date,
        "end_date": end_date,
        "weekly_plan": weekly_plan
    }
    return Response(response_data, status= status.HTTP_201_CREATED, content_type='application/json')

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def view_meal_plan(request, meal_plan_id):
    meal_plan = get_object_or_404(MealPlan, id=meal_plan_id, user=request.user)
    serializer = MealPlanSerializer(meal_plan)
    return Response({
        "meal_plan_id": serializer.data['id'],
        "creation_date": serializer.data["created_at"],
        "start_date": serializer.data["start_date"],
        "end_date": serializer.data["end_date"],
        "weekly_plan": serializer.data["daily_meals"]
        }, status=status.HTTP_200_OK, content_type='application/json')

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def view_daily_meal(request, meal_plan_id, day):
    meal_plan = get_object_or_404(MealPlan, id=meal_plan_id, user=request.user)
    target_date = meal_plan.start_date + timedelta(days=day-1)
    daily_meal = get_object_or_404(DailyMeal, meal_plan=meal_plan, date=target_date)
    serializer = DailyMealSerializer(daily_meal)
    return Response(serializer.data, status=status.HTTP_200_OK, content_type='application/json')

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_meal_plan(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return Response({"detail": "User profile not found"}, status=status.HTTP_404_NOT_FOUND, content_type='application/json')

    # Update user profile with the data from the request
    profile_data = request.data.get('profile', {})
    if profile_data:
        profile.update_detailed_info(
            age=profile_data.get('age', profile.age),
            weight=profile_data.get('weight', profile.weight),
            height=profile_data.get('height', profile.height),
            gender=profile_data.get('gender', profile.gender),
            body_fat=profile_data.get('body_fat', profile.body_fat),
            goal=profile_data.get('goal', profile.goal),
            lifestyle_intensity=profile_data.get('lifestyle_intensity', profile.lifestyle_intensity),
            recommended_calories=profile_data.get('recommended_calories', profile.recommended_calories)
        )

    # Delete the old meal plan
    # MealPlan.objects.filter(user=request.user).delete()

    # Initialize and run the expert system
    expert_system = NutritionExpertSystem()
    expert_system.reset()
    expert_system.declare(User(
        age=profile.age,
        gender=profile.gender,
        weight=profile.weight,
        height=profile.height,
        body_fat=profile.body_fat,
        goal=profile.goal,
        lifestyle_intensity=profile.lifestyle_intensity,
        recommended_calories=profile.recommended_calories
    ))
    expert_system.run()

    # Extract the weekly meal plan from the expert system
    weekly_plan = expert_system.weekly_plan if hasattr(expert_system, 'weekly_plan') else None
    
    if not weekly_plan:
        return Response({"detail": "Failed to generate meal plan"}, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

    # Create new MealPlan and DailyMeal objects
    start_date = date.today()
    end_date = start_date + timedelta(days=6)

    meal_plan = MealPlan.objects.create(
        user=request.user,
        start_date=start_date,
        end_date=end_date
    )

    for i, daily_meals in enumerate(weekly_plan):
        DailyMeal.objects.create(
            meal_plan=meal_plan,
            date=start_date + timedelta(days=i),
            meals=daily_meals
        )

    # Use serializers to format the response data
    meal_plan_serializer = MealPlanSerializer(meal_plan)
    daily_meals_serializer = DailyMealSerializer(meal_plan.daily_meals.all(), many=True)

    # Prepare the response data
    response_data = {
        "message": "Meal plan updated successfully",
        "meal_plan": meal_plan_serializer.data,
        "daily_meals": daily_meals_serializer.data
    }

    return Response(response_data, status=status.HTTP_205_RESET_CONTENT, content_type='application/json')

@api_view(['POST', 'PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def generate_update_recipe(request):
    print(json.dumps(request.data, indent=2))
    input_serializer = RecipeInputSerializer(data=request.data)
    if input_serializer.is_valid():
        name = input_serializer.validated_data['name']
        nutrition_facts = input_serializer.validated_data['nutrition_facts']

        # Generate recipe using the provided name and nutrition facts
        try:
            recipe_data = generate_recipe(name,nutrition_facts)
            print(json.dumps(recipe, indent=2))
        except Exception as e:
            print(f"cohere error occurred: {e}")
        
        recipe, created = Recipe.objects.update_or_create(
            name=name,
            defaults={
                'ingredients': recipe_data['ingredients'],
                'instructions': recipe_data['instructions'],
                'nutrition_facts': nutrition_facts
            }
        )

        serializer = RecipeSerializer(recipe)
        action = 'created' if created else 'updated'
        st = status.HTTP_201_CREATED if action == 'created' else status.HTTP_202_ACCEPTED
        return Response({'message': f'Recipe {action} successfully', 'recipe': serializer.data}, status=st, content_type='application/json')
    return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def view_recipe(request):
    name = request.data.get('name', '')
    try:
        recipe = Recipe.objects.get(name__iexact=name)
        serializer = RecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_200_OK, content_type='application/json')
    except Recipe.DoesNotExist:
        return Response({'error': 'Recipe not found'}, status=status.HTTP_404_NOT_FOUND, content_type='application/json')