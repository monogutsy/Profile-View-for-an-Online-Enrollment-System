from django.contrib import admin

from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("student_number", "full_name", "course", "year_level", "class_section")
    list_filter = ("class_section",)
    search_fields = ("student_number", "first_name", "last_name")
