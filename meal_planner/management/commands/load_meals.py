import csv
from django.core.management.base import BaseCommand
from meals.models import Meal

class Command(BaseCommand):
    help = 'Load meals data from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        meals = []

        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                meal = Meal(
                    category=row['category'],
                    meal=row['meal'],
                    calories=float(row['calories']),
                    carbohydrates=float(row['carbohydrates']),
                    protein=float(row['protein']),
                    fat=float(row['fat'])
                )
                meals.append(meal)

        Meal.objects.bulk_create(meals)
        self.stdout.write(self.style.SUCCESS(f'Successfully loaded {len(meals)} meals'))
