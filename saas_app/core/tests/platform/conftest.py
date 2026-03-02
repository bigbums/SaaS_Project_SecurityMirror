# core/tests/platform/conftest.py
import pytest
from django.contrib.auth import get_user_model
from saas_app.core.models import PlatformUser, PlatformInvoice
from saas_app.core.tests.factories import UserFactory

User = get_user_model()

@pytest.fixture
def platform_test_user(db):
    return User.objects.create_user(email="platformuser@example.com", password="pass123")

@pytest.fixture
def platform_user(db, platform_test_user):
    return PlatformUser.objects.create(user=platform_test_user)

@pytest.fixture
def platform_invoice_paid(db):
    return PlatformInvoice.objects.create(
        status="paid",
        amount=200,
        currency="USD"
    )

@pytest.fixture
def platform_invoice_unpaid(db):
    return PlatformInvoice.objects.create(
        status="unpaid",
        amount=200,
        currency="USD"
    )
