import pytest
from django.contrib.auth import get_user_model
from saas_app.core.models import Tenant, TenantUser, Tier
from saas_app.core.tests.factories import UserFactory

User = get_user_model()

@pytest.mark.django_db
def test_subscription_plan_for_tenant_standard():
    user = UserFactory(email="standard@example.com")

    # ✅ Reuse seeded tier
    tier = Tier.objects.get(name="Standard")

    tenant = Tenant.objects.create(name="Standard Tenant", email="std@example.com", tier=tier)
    TenantUser.objects.create(tenant=tenant, user=user, role="owner")

    assert tenant.tier.name == "Standard"
    assert tenant.tier.max_users > 0
    assert tenant.users.filter(user=user).exists()


@pytest.mark.django_db
def test_subscription_plan_for_tenant_premium():
    user = UserFactory(email="premium@example.com")

    # ✅ Reuse seeded tier
    tier = Tier.objects.get(name="Premium")

    tenant = Tenant.objects.create(name="Premium Tenant", email="prem@example.com", tier=tier)
    TenantUser.objects.create(tenant=tenant, user=user, role="owner")

    assert tenant.tier.name == "Premium"
    assert tenant.tier.max_users >= 10  # adjust based on your Tier definition
    assert tenant.users.filter(user=user).exists()
