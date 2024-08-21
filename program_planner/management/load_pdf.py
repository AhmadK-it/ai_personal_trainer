import csv
from django.core.management.base import BaseCommand
from program_planner.models import PDFFile

class Command(BaseCommand):
    help = 'Import data from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        url_data = []
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                pdf = PDFFile(
                        file_name=str(row['name']),
                        file_path=row['path']
                    )
                url_data.append(pdf)

        PDFFile.objects.bulk_create(url_data)
        self.stdout.write(self.style.SUCCESS(f'Successfully imported data from {csv_file}'))