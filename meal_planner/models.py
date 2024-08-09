from django.db import models


class Meal(models.Model):
    category = models.CharField(max_length=20)
    meal = models.CharField(max_length=255)
    calories = models.FloatField()
    carbohydrates = models.FloatField()
    protein = models.FloatField()
    fat = models.FloatField()

    def __str__(self):
        return f"{self.category}: {self.meal}"