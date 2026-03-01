import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from saas_app.core.models import Tier, Tenant, TenantUser
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_tenant_creation_with_standard_tier():
    user = User.objects.create_user(email="tenantuser@example.com", password="pass123")
    tier = Tier.objects.get(name="Standard")
    tenant = Tenant.objects.create(name="Tenant SME", email="tenant@example.com", tier=tier)
    TenantUser.objects.create(tenant=tenant, user=user, role="owner")

    assert tenant.name == "Tenant SME"
    assert tenant.tier.name == "Standard"
    assert tenant.users.filter(user=user).exists()

@pytest.mark.django_db
def test_tenant_creation_with_premium_tier():
    user = User.objects.create_user(email="premiumtenant@example.com", password="pass123")
    tier = Tier.objects.get(name="Premium")
    tenant = Tenant.objects.create(name="Premium Tenant", email="premtenant@example.com", tier=tier)
    TenantUser.objects.create(tenant=tenant, user=user, role="owner")

    assert tenant.tier.name == "Premium"
    assert tenant.tier.max_users >= 10
    assert tenant.users.filter(user=user).exists()

@pytest.mark.django_db
def test_tenant_detail():
    client = APIClient()
    user = User.objects.create_user(email="alice@example.com", password="pass123")
    client.force_authenticate(user=user)

    tier = Tier.objects.get(name="Free")
    tenant = Tenant.objects.create(name="Tenant A", email="tenantA@example.com", tier=tier)
    TenantUser.objects.create(tenant=tenant, user=user, role="owner")

    url = reverse("v1:tenant-detail", args=[tenant.id])
    response = client.get(url)
    assert response.status_code == 200
    assert response.data["name"] == "Tenant A"
