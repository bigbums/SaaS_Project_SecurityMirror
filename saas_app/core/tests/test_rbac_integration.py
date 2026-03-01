# saas_app/core/tests/test_rbac_integration.py

import pytest
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from saas_app.core.models import Tenant, TenantUser, PlatformUser, Tier
from saas_app.core.middleware.TenantMiddleware import TenantMiddleware
from saas_app.core.middleware.rbac_middleware import RBACMiddleware
from saas_app.core.viewsets.viewsets import TenantInvoiceViewSet, PlatformInvoiceViewSet
from saas_app.core.config.privileges import role_privileges

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.parametrize("role,action,expected_allowed", [
    ("owner", "create", True),      # Tenant owner can create invoices
    ("admin", "create", False),     # Tenant admin cannot create invoices
])
def test_tenant_invoice_rbac(role, action, expected_allowed):
    user = User.objects.create_user(email=f"{role}@example.com", password="pass123")
    tier = Tier.objects.get(name="Standard")
    tenant = Tenant.objects.create(name=f"{role}-tenant", email=f"{role}@example.com", tier=tier)
    TenantUser.objects.create(user=user, tenant=tenant, role=role)

    request = RequestFactory().get("/")
    request.user = user
    request = TenantMiddleware(lambda req: req)(request)
    request = RBACMiddleware(lambda req: req)(request)

    viewset = TenantInvoiceViewSet()
    viewset.action = action
    required_privilege = viewset.get_required_privilege()

    allowed = required_privilege in getattr(request.user, "permissions", [])
    assert allowed == expected_allowed


@pytest.mark.django_db
@pytest.mark.parametrize("role,action,expected_allowed", [
    ("platform_admin", "update", False),   # Platform admin cannot update invoices
    ("platform_admin", "list", True),      # Platform admin can list invoices
    ("platform_admin", "retrieve", True),  # Platform admin can retrieve invoices
])
def test_platform_invoice_rbac(role, action, expected_allowed):
    user = User.objects.create_user(email=f"{role}@example.com", password="pass123")
    PlatformUser.objects.create(user=user, role=role)

    request = RequestFactory().get("/")
    request.user = user
    request = TenantMiddleware(lambda req: req)(request)
    request = RBACMiddleware(lambda req: req)(request)

    viewset = PlatformInvoiceViewSet()
    viewset.action = action
    required_privilege = viewset.get_required_privilege()

    allowed = required_privilege in getattr(request.user, "permissions", [])
    assert allowed == expected_allowed



@pytest.mark.django_db
@pytest.mark.parametrize("role", list(role_privileges.keys()))
@pytest.mark.parametrize("action", ["list", "retrieve", "create", "update", "partial_update", "destroy"])
def test_rbac_pipeline_all_roles(role, action):
    """
    Parametrized integration test: verifies that for every role and every invoice action,
    the middleware attaches permissions and the ViewSet enforces them correctly.
    """
    user = User.objects.create_user(email=f"{role}@example.com", password="pass123")

    # Create either a PlatformUser or TenantUser depending on role
    if role.startswith("platform"):
        PlatformUser.objects.create(user=user, role=role)
        viewset = PlatformInvoiceViewSet()
    else:
        tier = Tier.objects.get(name="Standard")
        tenant = Tenant.objects.create(name=f"{role}-tenant", email=f"{role}@example.com", tier=tier)
        TenantUser.objects.create(user=user, tenant=tenant, role=role)
        viewset = TenantInvoiceViewSet()

    # Simulate request through both middlewares
    request = RequestFactory().get("/")
    request.user = user
    request = TenantMiddleware(lambda req: req)(request)
    request = RBACMiddleware(lambda req: req)(request)

    # Simulate ViewSet action
    viewset.action = action
    required_privilege = viewset.get_required_privilege()

    if required_privilege:
        allowed = required_privilege in getattr(request.user, "permissions", [])
        # Assert consistency: if privilege is required, user must have it to be allowed
        assert allowed == (required_privilege in role_privileges[role])
    else:
        # If no privilege is mapped for this action, test should confirm None
        assert required_privilege is None
