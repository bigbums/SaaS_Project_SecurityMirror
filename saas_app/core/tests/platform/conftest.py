import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from saas_app.core.models import Tenant, Tier, TenantUser, TenantCustomer

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def tenant_and_user(db):
    custom_user = User.objects.create_user(email="tenantuser@example.com", password="pass123")
    tier = Tier.objects.get(name="Standard")
    tenant = Tenant.objects.create(email=custom_user.email, tier=tier)
    tenant_user = TenantUser.objects.create(user=custom_user, tenant=tenant)
    return tenant, tenant_user, custom_user

@pytest.fixture
def tenant_customer(db, tenant_and_user):
    tenant, _, _ = tenant_and_user
    return TenantCustomer.objects.create(
        tenant=tenant,
        name="Test Customer",
        email="customer@example.com"
    )
