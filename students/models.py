from django.db import models


class Student(models.Model):
    student_number = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    class_section = models.CharField("class / section", max_length=50)
    course = models.CharField(max_length=150)
    year_level = models.PositiveSmallIntegerField()
    date_of_birth = models.DateField(blank=True, null=True)
    email = models.EmailField(blank=True)
    contact_number = models.CharField(max_length=30, blank=True)
    home_address = models.TextField(blank=True)
    previous_school = models.CharField(max_length=200, blank=True)
    guardian_name = models.CharField(max_length=200, blank=True)
    guardian_contact_number = models.CharField(max_length=30, blank=True)

    class Meta:
        ordering = ["last_name", "first_name", "student_number"]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.student_number} - {self.full_name}"
