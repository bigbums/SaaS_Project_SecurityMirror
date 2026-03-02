import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

User = get_user_model()

@pytest.mark.django_db
def test_user_list():
    client = APIClient()
    user = User.objects.create_user(email="alice@example.com", password="pass123")
    client.force_authenticate(user=user)

    url = reverse("v1:user-list")
    response = client.get(url)
    assert response.status_code == 200
    assert any(u["email"] == "alice@example.com" for u in response.data)
