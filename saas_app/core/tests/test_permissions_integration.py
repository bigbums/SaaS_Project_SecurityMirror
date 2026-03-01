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
def test_permissions_integration(tier_name, branding_expected, invoice_expected):
    # Get seeded tier
    tier = Tier.objects.get(name=tier_name)

    # Create user and tenant tied to this tier
    user = UserFactory(email=f"{tier_name.lower()}@example.com")
    tenant = TenantFactory(email=user.email, tier=tier)
    tenant_user = TenantUser.objects.create(tenant=tenant, user=user, role="owner")

    # Build request with user
    request = APIRequestFactory().get("/")
    request.user = user
    request.tenant = tenant # ✅ force correct tenant context

    # Debug prints
    print("Tier:", tier.name, tier.features)
    print("TenantUser:", tenant_user)

    # Permissions check (integration style)
    branding_perm = RequireBrandingPermission()
    invoice_perm = RequireInvoiceCustomizationPermission()

    assert branding_perm.has_permission(request, None) is branding_expected
    assert invoice_perm.has_permission(request, None) is invoice_expected
