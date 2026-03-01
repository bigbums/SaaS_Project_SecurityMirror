# saas_app/core/tests/test_middlewares.py

import pytest
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from saas_app.core.models import Tenant, TenantUser, PlatformUser, Tier
from saas_app.core.middleware.TenantMiddleware import TenantMiddleware
from saas_app.core.middleware.rbac_middleware import RBACMiddleware
from saas_app.core.config.privileges import role_privileges

User = get_user_model()



@pytest.mark.django_db
def test_tenant_middleware_platform_user_has_no_tenant():
    user = User.objects.create_user(email="platform@example.com", password="pass123")
    PlatformUser.objects.create(user=user, role="platform_admin")

    request = RequestFactory().get("/")
    request.user = user

    middleware = TenantMiddleware(lambda req: req)
    request = middleware(request)

    assert request.tenant is None

@pytest.mark.django_db
def test_tenant_middleware_assigns_tenant_to_tenant_user():
    user = User.objects.create_user(email="tenant@example.com", password="pass123")
    tier = Tier.objects.get(name="Standard")
    tenant = Tenant.objects.create(name="Tenant A", email="tenant@example.com", tier=tier)
    TenantUser.objects.create(user=user, tenant=tenant, role="admin")

    request = RequestFactory().get("/")
    request.user = user

    middleware = TenantMiddleware(lambda req: req)
    request = middleware(request)

    assert request.tenant == tenant


@pytest.mark.django_db
def test_rbac_middleware_assigns_permissions_for_platform_user():
    user = User.objects.create_user(email="platform@example.com", password="pass123")
    PlatformUser.objects.create(user=user, role="platform_admin")

    request = RequestFactory().get("/")
    request.user = user

    tenant_middleware = TenantMiddleware(lambda req: req)
    rbac_middleware = RBACMiddleware(lambda req: req)

    request = tenant_middleware(request)
    request = rbac_middleware(request)

    assert "invoice:view" in request.user.permissions
    assert set(request.user.permissions) == set(role_privileges["platform_admin"])


@pytest.mark.django_db
def test_rbac_middleware_assigns_permissions_for_tenant_user():
    user = User.objects.create_user(email="tenant@example.com", password="pass123")
    tier = Tier.objects.get(name="Standard")  # use seeded tier
    tenant = Tenant.objects.create(name="Tenant B", email="tenant@example.com", tier=tier)
    TenantUser.objects.create(user=user, tenant=tenant, role="owner")

    request = RequestFactory().get("/")
    request.user = user

    tenant_middleware = TenantMiddleware(lambda req: req)
    rbac_middleware = RBACMiddleware(lambda req: req)

    request = tenant_middleware(request)
    request = rbac_middleware(request)

    assert "invoice:create" in request.user.permissions
    assert set(request.user.permissions) == set(role_privileges["owner"])


@pytest.mark.django_db
@pytest.mark.parametrize("role", list(role_privileges.keys()))
def test_rbac_middleware_assigns_permissions_for_each_role(role):
    """
    Parametrized test: verifies that RBACMiddleware assigns the correct
    permissions for every role defined in role_privileges.
    """
    user = User.objects.create_user(email=f"{role}@example.com", password="pass123")

    # Create either a PlatformUser or TenantUser depending on role
    if role.startswith("platform"):
        PlatformUser.objects.create(user=user, role=role)
    else:
        tier = Tier.objects.get(name="Standard")
        tenant = Tenant.objects.create(name=f"{role}-tenant", email=f"{role}@example.com", tier=tier)
        TenantUser.objects.create(user=user, tenant=tenant, role=role)

    request = RequestFactory().get("/")
    request.user = user

    tenant_middleware = TenantMiddleware(lambda req: req)
    rbac_middleware = RBACMiddleware(lambda req: req)

    # Pass through both middlewares
    request = tenant_middleware(request)
    request = rbac_middleware(request)

    # Assert permissions match exactly what role_privileges defines
    assert set(request.user.permissions) == set(role_privileges[role])
