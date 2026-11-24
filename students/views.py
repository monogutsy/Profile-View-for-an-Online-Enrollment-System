from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import never_cache

from .models import Student


@never_cache
def student_list(request):
    sections = (
        Student.objects.order_by("class_section")
        .values_list("class_section", flat=True)
        .distinct()
    )
    selected_section = request.GET.get("section", sections.first() or "")
    students = Student.objects.filter(class_section=selected_section)
    return render(
        request,
        "students/student_list.html",
        {
            "students": students,
            "sections": sections,
            "selected_section": selected_section,
        },
    )


@never_cache
def student_detail(request, pk):
    students = Student.objects.all()
    selected_section = request.GET.get("section")
    if selected_section is not None:
        students = students.filter(class_section=selected_section)
    student = get_object_or_404(students, pk=pk)
    return render(request, "students/student_detail.html", {"student": student})
