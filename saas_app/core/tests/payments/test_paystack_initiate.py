import pytest
from django.urls import reverse
from unittest.mock import patch
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from saas_app.core.models import Tenant, Tier

User = get_user_model()

@pytest.mark.django_db
class PaystackInitiateViewTests:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="test@example.com", password="pass")
        self.client.force_authenticate(user=self.user)

        # Always use Free tier by default
        self.tier = Tier.objects.get(name="Free")
        self.tenant = Tenant.objects.create(name="TestCo", email="test@example.com", tier=self.tier)

    @patch("requests.post")
    def test_initiate_paystack_success(self, mock_post):
        mock_post.return_value.json.return_value = {
            "status": True,
            "data": {
                "reference": "PSK123",
                "authorization_url": "https://paystack.com/checkout/PSK123"
            }
        }

        url = reverse("initiate_paystack_payment", args=[self.tenant.id, self.tier.id])
        response = self.client.get(url)

        assert response.status_code in (302, 303)
        assert response.url == "https://paystack.com/checkout/PSK123"

    @patch("requests.post")
    def test_initiate_paystack_failure(self, mock_post):
        mock_post.return_value.json.return_value = {"status": False}

        url = reverse("initiate_paystack_payment", args=[self.tenant.id, self.tier.id])
        response = self.client.get(url)

        assert response.status_code in (302, 303)
        assert response.url == reverse("dashboard")
