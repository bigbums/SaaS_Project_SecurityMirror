import pytest
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from django.contrib.auth import get_user_model
from saas_app.core.models import Tenant, TenantUser, Tier, PlatformInvoice, TenantInvoice, TenantCustomer

User = get_user_model()

@pytest.mark.django_db
def test_smoke_routes_and_permissions():
    client = APIClient()

    # Create users
    admin = User.objects.create_user(email="admin@example.com", password="pass123")
    viewer = User.objects.create_user(email="viewer@example.com", password="pass123")

    # Create tenant + tier
    tier = Tier.objects.get(name="Free")
    tenant = Tenant.objects.create(name="Tenant A", email="tenantA@example.com", tier=tier)

    # Link users to tenant
    TenantUser.objects.create(tenant=tenant, user=admin, role="owner")
    TenantUser.objects.create(tenant=tenant, user=viewer, role="member")

    # Create a customer for the tenant
    customer = TenantCustomer.objects.create(tenant=tenant, name="Customer A", email="cust@example.com")

    # Create invoices
    platform_invoice = PlatformInvoice.objects.create(
        tenant=tenant,
        amount=100,
        currency="USD",
        due_date="2026-03-01",
        status="unpaid"
    )
    tenant_invoice = TenantInvoice.objects.create(
        tenant=tenant,
        customer=customer,   # 👈 attach customer here
        amount=200,
        currency="USD",
        due_date="2026-03-01",
        status="unpaid"
    )

    # --- Test TenantInvoice list ---
    client.force_authenticate(user=admin)
    url = reverse("v1:tenantinvoice-list")
    response = client.get(url)
    print("TenantInvoice list (admin):", response.status_code, response.data)

    # --- Test Tenant detail ---
    url = reverse("v1:tenant-detail", args=[tenant.id])
    response = client.get(url)
    print("Tenant detail (admin):", response.status_code, response.data)

    # --- Test PlatformInvoice mark_paid ---
    url = reverse("v1:platforminvoice-mark-paid", args=[platform_invoice.id])
    response = client.patch(url)
    print("PlatformInvoice mark_paid (admin):", response.status_code, response.data)

    # --- Test member read-only ---
    client.force_authenticate(user=viewer)
    url = reverse("v1:tenantinvoice-list")
    response = client.post(url, {
        "tenant": tenant.id,
        "customer": customer.id,   # 👈 include customer ID
        "amount": 300,
        "currency": "USD",
        "due_date": "2026-03-01",
        "status": "unpaid"
    }, format="json")
    print("TenantInvoice create (viewer):", response.status_code, response.data)
