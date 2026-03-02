# core/tests/conftest.py
import pytest
from rest_framework.test import APIClient
from django.core.management import call_command
from saas_app.core.models import Tier

@pytest.fixture(scope="session", autouse=True)
def load_tiers_fixture(django_db_setup, django_db_blocker):
    """
    Load tiers.json only if no tiers exist.
    Prevents duplicate key errors when tiers are already seeded via migrations.
    """
    with django_db_blocker.unblock():
        if Tier.objects.count() == 0:
            call_command("loaddata", "tiers.json")

@pytest.fixture
def api_client():
    """Reusable DRF API client for all tests."""
    return APIClient()

@pytest.fixture
def tier_standard(db):
    """Standard tier fixture available to both tenant and platform tests."""
    return Tier.objects.get_or_create(
        name="Standard",
        defaults={"max_users": 10, "max_locations": 2, "price": 0, "hosting_type": "cloud"},
    )[0]
