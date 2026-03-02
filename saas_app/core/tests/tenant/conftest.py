# core/tests/tenant/conftest.py
import pytest
from django.contrib.auth import get_user_model
from saas_app.core.models import Tenant, TenantUser, Tier
from saas_app.core.tests.factories import UserFactory, TenantFactory
from saas_app.core.tests.conftest import tier_standard

User = get_user_model()

@pytest.fixture
def tenant_test_user(db):
    return User.objects.create_user(email="tenantuser@example.com", password="pass123")

@pytest.fixture
def tenant_test_tenant(db, tenant_test_user, tier_standard):
    tenant, _ = Tenant.objects.get_or_create(
        email=tenant_test_user.email,
        defaults={"tier": tier_standard}
    )
    tenant.tier = tier_standard
    tenant.save()
    return tenant

@pytest.fixture
def tenant_user(db, tenant_test_tenant, tenant_test_user):
    return TenantUser.objects.create(tenant=tenant_test_tenant, user=tenant_test_user, role="admin")

@pytest.fixture
def tenant_users(db):
    return [UserFactory(email=f"tenant_user{i}@example.com") for i in range(5)]

@pytest.fixture
def tenant(db, tenant_users):
    return TenantFactory(email=tenant_users[0].email, tier=tier_standard)
