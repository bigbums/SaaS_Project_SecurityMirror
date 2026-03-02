import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from saas_app.core.models import Tenant, TenantUser, TenantInvoice, Tier, TenantCustomer
from datetime import date

User = get_user_model()

@pytest.mark.django_db
def test_invoices_are_scoped_to_tenant():
    client = APIClient()
    owner1 = User.objects.create_user(email="owner1@example.com", password="pass123")
    owner2 = User.objects.create_user(email="owner2@example.com", password="pass123")

    tier = Tier.objects.get(name="Free")
    tenant1 = Tenant.objects.create(name="Tenant1", email="t1@example.com", tier=tier)
    tenant2 = Tenant.objects.create(name="Tenant2", email="t2@example.com", tier=tier)

    TenantUser.objects.create(tenant=tenant1, user=owner1, role="owner")
    TenantUser.objects.create(tenant=tenant2, user=owner2, role="owner")

    customer1 = TenantCustomer.objects.create(tenant=tenant1, name="Cust1", email="c1@example.com")
    customer2 = TenantCustomer.objects.create(tenant=tenant2, name="Cust2", email="c2@example.com")

    TenantInvoice.objects.create(
        tenant=tenant1, customer=customer1, amount=100, currency="NGN",
        due_date=date(2026, 2, 15), status="paid"
    )
    TenantInvoice.objects.create(
        tenant=tenant2, customer=customer2, amount=200, currency="NGN",
        due_date=date(2026, 2, 20), status="unpaid"
    )

    client.force_authenticate(user=owner1)
    url = reverse("v1:tenantinvoice-list")
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 1

    client.force_authenticate(user=owner2)
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 1
