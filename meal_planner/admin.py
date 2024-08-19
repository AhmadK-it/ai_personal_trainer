from django.contrib import admin
from .models import Meal, MealPlan, Recipe

admin.site.register(Meal)
admin.site.register(MealPlan)
admin.site.register(Recipe)