import pytest
from django.contrib.auth import get_user_model
from saas_app.core.models import Tenant, Tier
from unittest.mock import MagicMock

User = get_user_model()

@pytest.fixture
def test_user(db):
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )

@pytest.fixture
def test_tenant(db, test_user):
    return Tenant.objects.create(
        name="TestCo",
        email=test_user.email,
        owner=test_user
    )

@pytest.fixture
def test_tier(db):
    return Tier.objects.create(name="Pro", price=1000)

@pytest.fixture
def logged_in_client(client, test_user):
    client.force_login(test_user)
    return client

# Mock API responses
@pytest.fixture
def paystack_success_response():
    fake = MagicMock()
    fake.json.return_value = {
        "status": True,
        "data": {
            "reference": "PSK123",
            "authorization_url": "https://paystack.com/checkout/PSK123",
            "status": "success"
        }
    }
    return fake

@pytest.fixture
def paystack_failure_response():
    fake = MagicMock()
    fake.json.return_value = {"status": True, "data": {"status": "failed"}}
    return fake

@pytest.fixture
def opay_success_response():
    fake = MagicMock()
    fake.json.return_value = {
        "code": "0000",
        "data": {
            "cashierUrl": "https://opay.com/cashier/OP123",
            "status": "SUCCESS"
        }
    }
    return fake

@pytest.fixture
def opay_failure_response():
    fake = MagicMock()
    fake.json.return_value = {"code": "9999", "data": {"status": "FAILED"}}
    return fake
