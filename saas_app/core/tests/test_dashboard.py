import pytest
from django.contrib.auth import get_user_model
from saas_app.core.models import Tier, Tenant, TenantUser

User = get_user_model()

@pytest.mark.django_db
def test_dashboard_tenant_tier():
    # Create a user
    user = User.objects.create_user(email="test@example.com", password="pass123")

    # Attach user to a tenant with a specific tier
    tier = Tier.objects.get(name="Standard")
    tenant = Tenant.objects.create(name="Demo Tenant", email="tenant@example.com", tier=tier)
    TenantUser.objects.create(tenant=tenant, user=user, role="owner")

    # Assertions
    assert tenant.name == "Demo Tenant"
    assert tenant.tier.name == "Standard"
    assert tenant.users.filter(user=user).exists()

