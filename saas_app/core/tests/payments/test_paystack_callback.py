import pytest
from django.urls import reverse
from unittest.mock import patch
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class PaystackCallbackViewTests:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="test@example.com", password="pass")
        self.client.force_authenticate(user=self.user)

    @patch("requests.get")
    def test_paystack_callback_success(self, mock_get):
        mock_get.return_value.json.return_value = {
            "status": True,
            "data": {"status": "success"}
        }
        response = self.client.get(reverse("paystack_callback"), {"reference": "PSK123"})
        assert response.status_code in (302, 303)
        assert response.url == reverse("dashboard")

    @patch("requests.get")
    def test_paystack_callback_failure(self, mock_get):
        mock_get.return_value.json.return_value = {
            "status": True,
            "data": {"status": "failed"}
        }
        response = self.client.get(reverse("paystack_callback"), {"reference": "PSK123"})
        assert response.status_code in (302, 303)
        assert response.url == reverse("dashboard")
