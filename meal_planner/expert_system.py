from experta import *
from .models import Meal
from django.db.models import Q
import random

class User(Fact):
    """Information about the user"""
    pass

class MealPlan(Fact):
    """Calculated meal plan"""
    pass

class NutritionExpertSystem(KnowledgeEngine):
    
    def __init__(self):
        super().__init__()
        self.weekly_plan = None
    
    @DefFacts()
    def initial_facts(self):
        yield Fact(action="calculate_bmr")

    @Rule(Fact(action="calculate_bmr"),
          User(age=MATCH.age, gender=MATCH.gender, weight=MATCH.weight, height=MATCH.height))
    def calculate_bmr(self, age, gender, weight, height):
        if gender == 'male':
            bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        else:
            bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
        self.declare(Fact(bmr=bmr))
        self.declare(Fact(action="calculate_recommended_calories"))
        
    @Rule(Fact(action="calculate_recommended_calories"),
          User(recommended_calories=MATCH.recommended_calories),
          Fact(bmr=MATCH.bmr))
    def calculate_recommended_calories(self, recommended_calories, bmr):
        if recommended_calories != 0:
            final_calories = ((bmr * 1.2) + recommended_calories) / 2
        else:
            final_calories = bmr * 1.2
        self.declare(Fact(final_calories=final_calories))
        self.declare(Fact(action="adjust_calories_lifestyle"))

    @Rule(Fact(action="adjust_calories_lifestyle"),
          User(lifestyle_intensity=MATCH.intensity),
          Fact(final_calories=MATCH.calories))
    def adjust_calories_lifestyle(self, intensity, calories):
        intensity_multipliers = {
            'sedentary': 1.2,
            'moderate': 1.5,
            'intensive': 1.7
        }
        adjusted_calories = calories * intensity_multipliers.get(intensity, 1.2)
        self.declare(Fact(adjusted_calories=adjusted_calories))
        self.declare(Fact(action="adjust_calories_goal"))

    @Rule(Fact(action="adjust_calories_goal"),
          User(goal=MATCH.goal, body_fat=MATCH.body_fat),
          Fact(adjusted_calories=MATCH.calories))
    def adjust_calories_goal(self, goal, body_fat, calories):
        goal_adjustments = {
            'weight_loss': -400,
            'weight_gain': 200,
            'muscle_gain': 200
        }
        final_calories = calories + goal_adjustments.get(goal, 0)

        if goal == 'weight_loss' and body_fat > 30:
            final_calories -= 100
        elif goal == 'weight_gain' and body_fat < 10:
            final_calories += 200

        protein_multiplier = 1.7 if goal == 'muscle_gain' else 1.5 if goal == 'weight_gain' else 1
        fat_multiplier = 1.2 if goal == 'muscle_gain' else 1.1 if goal == 'weight_gain' else 1

        self.declare(MealPlan(calories=final_calories,
                              protein_multiplier=protein_multiplier,
                              fat_multiplier=fat_multiplier))
        self.declare(Fact(action="generate_meal_plan"))

    @Rule(Fact(action="generate_meal_plan"),
          MealPlan(calories=MATCH.calories, protein_multiplier=MATCH.protein_mult, fat_multiplier=MATCH.fat_mult),
          User(weight=MATCH.weight))
    def generate_meal_plan(self, calories, protein_mult, fat_mult, weight):
        protein_target = weight * protein_mult
        fat_target = weight * fat_mult
        carb_target = (calories - (protein_target * 4 + fat_target * 9)) / 4

        self.weekly_plan = self.generate_weekly_meal_plan(calories, protein_target, fat_target, carb_target)
        self.print_weekly_meal_plan(self.weekly_plan)

    def generate_weekly_meal_plan(self, daily_calories, protein_target, fat_target, carb_target):
        weekly_plan = []
        used_meals = set()

        for _ in range(7):  # 7 days in a week
            daily_plan = self.generate_daily_meal_plan(daily_calories, protein_target, fat_target, carb_target, used_meals)
            weekly_plan.append(daily_plan)
            used_meals.update(meal['name'] for meal in daily_plan)

        return weekly_plan

    def generate_daily_meal_plan(self, daily_calories, protein_target, fat_target, carb_target, used_meals):
        if daily_calories >= 3500:
            meal_counts = {'breakfast': 2, 'lunch': 2, 'dinner': 1, 'snacks': 3}
        elif 3000 <= daily_calories < 3500:
            meal_counts = {'breakfast': 1, 'lunch': 2, 'dinner': 1, 'snacks': 3}
        else:
            meal_counts = {'breakfast': 1, 'lunch': 1, 'dinner': 1, 'snacks': 2}

        daily_plan = []
        remaining_calories = daily_calories
        remaining_protein = protein_target
        remaining_fat = fat_target
        remaining_carbs = carb_target

        for meal_type, count in meal_counts.items():
            for _ in range(count):
                meal = self.select_meal(meal_type, remaining_calories / count, remaining_protein / count,
                                        remaining_fat / count, remaining_carbs / count, used_meals)
                if meal:
                    daily_plan.append(meal)
                    remaining_calories -= meal['calories']
                    remaining_protein -= meal['protein']
                    remaining_fat -= meal['fat']
                    remaining_carbs -= meal['carbohydrates']

        self.adjust_meal_portions(daily_plan, daily_calories, protein_target, fat_target, carb_target)

        return daily_plan

    def select_meal(self, meal_type, target_calories, target_protein, target_fat, target_carbs, used_meals):
        suitable_meals = Meal.objects.filter(
            Q(category=meal_type) &
            Q(calories__lte=target_calories * 1.2) &
            Q(protein__lte=target_protein * 1.2) &
            Q(fat__lte=target_fat * 1.2) &
            Q(carbohydrates__lte=target_carbs * 1.2) &
            ~Q(meal__in=used_meals)
        )

        if not suitable_meals.exists():
            return None

        selected_meal = random.choice(suitable_meals)
        return {
            'name': selected_meal.meal,
            'category': selected_meal.category,
            'calories': selected_meal.calories,
            'protein': selected_meal.protein,
            'fat': selected_meal.fat,
            'carbohydrates': selected_meal.carbohydrates
        }

    def adjust_meal_portions(self, daily_plan, target_calories, target_protein, target_fat, target_carbs):
        total_calories = sum(meal['calories'] for meal in daily_plan)
        total_protein = sum(meal['protein'] for meal in daily_plan)
        total_fat = sum(meal['fat'] for meal in daily_plan)
        total_carbs = sum(meal['carbohydrates'] for meal in daily_plan)

        calorie_ratio = target_calories / total_calories
        protein_ratio = target_protein / total_protein
        fat_ratio = target_fat / total_fat
        carb_ratio = target_carbs / total_carbs

        for meal in daily_plan:
            meal['calories'] *= calorie_ratio
            meal['protein'] *= protein_ratio
            meal['fat'] *= fat_ratio
            meal['carbohydrates'] *= carb_ratio

    def print_weekly_meal_plan(self, weekly_plan):
        for day, meals in enumerate(weekly_plan, 1):
            print(f"Day {day}:")
            for meal in meals:
                print(f"  {meal['category'].capitalize()}: {meal['name']}")
                print(f"    Calories: {meal['calories']:.2f}, Protein: {meal['protein']:.2f}g, Fat: {meal['fat']:.2f}g, Carbs: {meal['carbohydrates']:.2f}g")
