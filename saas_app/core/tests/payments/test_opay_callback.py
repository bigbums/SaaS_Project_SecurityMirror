import pytest
from django.urls import reverse
from unittest.mock import patch
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class OpayCallbackViewTests:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="test@example.com", password="pass")
        self.client.force_authenticate(user=self.user)

    @patch("requests.get")
    def test_opay_callback_success(self, mock_get):
        mock_get.return_value.json.return_value = {
            "status": True,
            "data": {"status": "SUCCESS"}
        }
        response = self.client.get(reverse("opay_callback"), {"reference": "OP123"})
        assert response.status_code in (302, 303)  # redirect
        assert response.url == reverse("dashboard")

    @patch("requests.get")
    def test_opay_callback_failure(self, mock_get):
        mock_get.return_value.json.return_value = {
            "status": True,
            "data": {"status": "FAILED"}
        }
        response = self.client.get(reverse("opay_callback"), {"reference": "OP123"})
        assert response.status_code in (302, 303)  # redirect
        assert response.url == reverse("dashboard")
