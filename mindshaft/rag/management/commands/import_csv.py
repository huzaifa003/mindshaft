import csv
from django.core.management.base import BaseCommand
from rag.models import Document
from datetime import datetime

class Command(BaseCommand):
    help = 'Import data from CSV file into Document model'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file = options['csv_file']

        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        # Parse the uploaded_at timestamp
                        

                        # Create the Document object
                        Document.objects.create(
                            title=row['title'],
                            file=row['file'],
                            
                        )

                        self.stdout.write(self.style.SUCCESS(f"Successfully imported: {row['title']}"))
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f"Error importing row {row}: {e}"))

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"File not found: {csv_file}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred: {e}"))
