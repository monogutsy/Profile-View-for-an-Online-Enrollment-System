from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from students.models import Student


class Command(BaseCommand):
    help = "Add the five fictional BSIT students, preserving existing records."

    @transaction.atomic
    def handle(self, *args, **options):
        records = [
            ("024A-2352", "Andrea Nicole", "Reyes", date(2006, 3, 15), "andrea.reyes@example.com", "Westhaven Senior High School", "Marissa Reyes"),
            ("024A-2353", "Miguel Antonio", "Santos", date(2006, 7, 22), "miguel.santos@example.com", "Northfield Senior High School", "Roberto Santos"),
            ("024A-2354", "Isabella Mae", "Cruz", date(2006, 1, 8), "isabella.cruz@example.com", "Eastbrook Senior High School", "Patricia Cruz"),
            ("024A-2355", "Gabriel Luis", "Mendoza", date(2005, 11, 12), "gabriel.mendoza@example.com", "Southridge Senior High School", "Elena Mendoza"),
            ("024A-2356", "Sofia Louise", "Ramos", date(2006, 9, 3), "sofia.ramos@example.com", "Greenvale Senior High School", "Ricardo Ramos"),
        ]
        created_count = 0
        for number, first, last, birth, email, school, guardian in records:
            student, created = Student.objects.get_or_create(
                student_number=number,
                defaults={
                    "first_name": first,
                    "last_name": last,
                    "course": "BSIT",
                    "class_section": "BSIT 1-A",
                    "year_level": 1,
                    "date_of_birth": birth,
                    "email": email,
                    "previous_school": school,
                    "guardian_name": guardian,
                },
            )
            created_count += created
        self.stdout.write(self.style.SUCCESS(f"Added {created_count} students; existing records preserved."))
