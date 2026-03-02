from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

# ✅ Import constants
from saas_app.core.tests.constants import LOGIN_PAGE_TEXT, SIGNUP_PAGE_TEXT

User = get_user_model()

class AuthViewTests(TestCase):
    def test_login_page_contains_expected_text(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        # ✅ Use constant instead of hardcoded "Login"
        self.assertContains(response, LOGIN_PAGE_TEXT)

    def test_signup_page_contains_expected_text(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)
        # ✅ Use constant instead of hardcoded "Sign Up"
        self.assertContains(response, SIGNUP_PAGE_TEXT)
