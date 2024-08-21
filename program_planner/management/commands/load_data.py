import csv
from django.core.management.base import BaseCommand
from program_planner.models import Program

class Command(BaseCommand):
    help = 'Import data from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file = options['csv_file']

        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            url_data = []
            for row in reader:
                program = Program(
                        index=int(row['index']),
                        url=row['url']
                    )
                url_data.append(program)

        Program.objects.bulk_create(url_data)
        self.stdout.write(self.style.SUCCESS(f'Successfully imported data from {csv_file}'))