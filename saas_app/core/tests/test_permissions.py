import pytest
from rest_framework.test import APIRequestFactory
from saas_app.core.tests.factories import UserFactory, TenantFactory
from saas_app.core.models import Tier, TenantUser
from saas_app.core.permissions import (
    RequireBrandingPermission,
    RequireInvoiceCustomizationPermission,
)

@pytest.mark.django_db
@pytest.mark.parametrize(
    "tier_name, branding_expected, invoice_expected",
    [
        ("Free", False, False),
        ("Standard", True, False),
        ("Premium", True, True),
        ("Enterprise", True, True),
    ],
)
def test_permissions_by_tier(tier_name, branding_expected, invoice_expected):
    # ✅ Get seeded tier directly
    tier = Tier.objects.get(name=tier_name)

    # Create user and tenant tied to this tier
    user = UserFactory(email=f"{tier_name.lower()}@example.com")
    tenant = TenantFactory(email=user.email, tier=tier)
    TenantUser.objects.create(tenant=tenant, user=user, role="owner")

    # Debug prints
    print("Tier:", tier.id, tier.name, tier.features)
    print("Tenant tier:", tenant.tier.id, tenant.tier.name, tenant.tier.features)
    print("User tenants:", list(user.tenants.all()))

    # Permissions check (feature-based)
    assert ("branding" in tenant.tier.features) == branding_expected
    assert ("invoice_customization" in tenant.tier.features) == invoice_expected
