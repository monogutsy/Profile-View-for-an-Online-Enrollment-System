from datetime import date
from io import StringIO

from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from .models import Student


class StudentPagesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ana = Student.objects.create(
            student_number="DEMO-001",
            first_name="Ana",
            last_name="Example",
            class_section="BSCS 1-A",
            course="BS Computer Science",
            year_level=1,
            date_of_birth=date(2006, 3, 15),
            email="ana@example.com",
            home_address="123 Sample Street, Fictional City",
            previous_school="Sample Senior High School",
        )
        cls.ben = Student.objects.create(
            student_number="DEMO-002",
            first_name="Ben",
            last_name="Sample",
            class_section="BSCS 1-A",
            course="BS Computer Science",
            year_level=1,
        )
        cls.other = Student.objects.create(
            student_number="DEMO-003",
            first_name="Casey",
            last_name="Test",
            class_section="BSIT 2-B",
            course="BS Information Technology",
            year_level=2,
        )

    def setUp(self):
        self.list_url = reverse("students:student_list")
        self.ana_url = reverse("students:student_detail", args=[self.ana.pk])

    def test_pages_open_without_login(self):
        for url in (self.list_url, self.ana_url):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, self.ana.full_name)
                self.assertNotContains(response, "Sign in")
                self.assertNotContains(response, "Sign out")

    def test_nonstaff_users_can_also_view_pages(self):
        user = get_user_model().objects.create_user(username="regular")
        self.client.force_login(user)
        for url in (self.list_url, self.ana_url):
            with self.subTest(url=url):
                self.assertContains(self.client.get(url), self.ana.full_name)

    def test_list_displays_only_the_default_class(self):
        response = self.client.get(self.list_url)
        self.assertContains(response, self.ana.full_name)
        self.assertContains(response, self.ben.full_name)
        self.assertNotContains(response, self.other.full_name)
        self.assertEqual(response.context["selected_section"], "BSCS 1-A")
        self.assertContains(response, "2 students in this class")

    def test_another_section_can_be_selected(self):
        response = self.client.get(self.list_url, {"section": self.other.class_section})
        self.assertContains(response, self.other.full_name)
        self.assertNotContains(response, self.ana.full_name)
        self.assertContains(
            response, '<option value="BSIT 2-B" selected>BSIT 2-B</option>', html=True
        )

    def test_profile_links_keep_the_class_scope(self):
        response = self.client.get(self.list_url)
        self.assertContains(response, f"{self.ana_url}?section=BSCS%201-A")
        self.assertContains(response, f"View Profile for {self.ana.full_name}")

    def test_each_profile_shows_only_its_own_information(self):
        response = self.client.get(self.ana_url)
        self.assertContains(response, self.ana.full_name)
        self.assertContains(response, "ana@example.com")
        self.assertContains(response, "March 15, 2006")
        self.assertContains(response, "Sample Senior High School")
        self.assertNotContains(response, self.ben.full_name)
        response = self.client.get(
            reverse("students:student_detail", args=[self.ben.pk])
        )
        self.assertContains(response, self.ben.full_name)
        self.assertNotContains(response, "ana@example.com")
        self.assertNotContains(response, self.ana.full_name)

    def test_profile_has_both_information_sections(self):
        response = self.client.get(self.ana_url)
        self.assertContains(response, "Personal Information")
        self.assertContains(response, "Background Information")

    def test_missing_optional_fields_are_labelled(self):
        response = self.client.get(
            reverse("students:student_detail", args=[self.ben.pk])
        )
        self.assertContains(response, "Not provided", count=7)
        self.assertNotContains(response, ">None<")

    def test_back_link_returns_to_the_same_class(self):
        response = self.client.get(
            reverse("students:student_detail", args=[self.other.pk])
        )
        self.assertContains(response, f'href="{self.list_url}?section=BSIT%202-B"')
        self.assertContains(
            response,
            f'<a class="back-link" href="{self.list_url}?section=BSIT%202-B">Back to Student List</a>',
            html=True,
        )

    def test_unknown_student_returns_404(self):
        response = self.client.get(reverse("students:student_detail", args=[999999]))
        self.assertEqual(response.status_code, 404)

    def test_student_outside_selected_class_returns_404(self):
        response = self.client.get(self.ana_url, {"section": self.other.class_section})
        self.assertEqual(response.status_code, 404)
        self.assertNotContains(response, "ana@example.com", status_code=404)

    def test_empty_class_has_a_clear_message(self):
        response = self.client.get(self.list_url, {"section": "Empty class"})
        self.assertContains(response, "No students found for this class.")
        self.assertContains(response, "0 students in this class")

    def test_empty_database_does_not_break_the_list(self):
        Student.objects.all().delete()
        self.assertContains(
            self.client.get(self.list_url), "No students found for this class."
        )

    def test_single_class_does_not_need_a_class_selector(self):
        self.other.delete()
        self.assertNotContains(self.client.get(self.list_url), '<select name="section"')

    def test_student_pages_are_not_cached(self):
        for url in (self.list_url, self.ana_url):
            with self.subTest(url=url):
                self.assertIn("no-store", self.client.get(url).headers["Cache-Control"])

    def test_stylesheet_exists_and_is_linked(self):
        self.assertIsNotNone(finders.find("css/style.css"))
        self.assertContains(
            self.client.get(self.list_url), 'href="/static/css/style.css"'
        )

    def test_root_opens_student_list(self):
        self.assertRedirects(self.client.get("/"), self.list_url)

    def test_activity_login_routes_are_removed(self):
        for url in ("/accounts/login/", "/accounts/logout/"):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 404)

    def test_student_number_must_be_unique(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Student.objects.create(
                student_number=self.ana.student_number,
                first_name="Duplicate",
                last_name="Example",
                class_section="BSCS 1-A",
                course="BS Computer Science",
                year_level=1,
            )


class SeedStudentsTests(TestCase):
    def test_seed_creates_five_students_and_can_be_repeated(self):
        call_command("seed_students", stdout=StringIO())
        call_command("seed_students", stdout=StringIO())
        self.assertEqual(Student.objects.count(), 5)
        self.assertEqual(Student.objects.filter(course="BSIT", class_section="BSIT 1-A").count(), 5)
        self.assertTrue(Student.objects.filter(student_number="024A-2352", first_name="Andrea Nicole").exists())

    def test_seed_preserves_existing_records(self):
        student = Student.objects.create(
            student_number="024A-2352", first_name="Updated name", last_name="Reyes",
            course="BSA", class_section="BSA 2-A", year_level=2,
        )
        call_command("seed_students", stdout=StringIO())
        student.refresh_from_db()
        self.assertEqual(student.first_name, "Updated name")
        self.assertEqual(student.course, "BSA")
