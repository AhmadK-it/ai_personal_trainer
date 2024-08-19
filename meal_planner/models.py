from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField

User = get_user_model()

class MealPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meal_plans')
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Meal Plan for {self.user.username} ({self.start_date} to {self.end_date})"

class DailyMeal(models.Model):
    meal_plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE, related_name='daily_meals')
    date = models.DateField()
    meals = models.JSONField()  # This will store the list of meals for the day

    def __str__(self):
        return f"Daily Meal for {self.meal_plan.user.username} on {self.date}"

class Meal(models.Model):
    category = models.CharField(max_length=20)
    meal = models.CharField(max_length=255)
    calories = models.FloatField()
    carbohydrates = models.FloatField()
    protein = models.FloatField()
    fat = models.FloatField()

    def __str__(self):
        return f"{self.category}: {self.meal}"

class Recipe(models.Model):
    name = models.CharField(max_length=200, unique=True)
    ingredients = models.JSONField()
    instructions = ArrayField(models.TextField())
    nutrition_facts = models.JSONField()

    def __str__(self):
        return self.name
