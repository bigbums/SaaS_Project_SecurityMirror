import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from saas_app.core.models import Tenant, TenantUser, TenantInvoice, Tier, TenantCustomer
from datetime import date
from django.urls import reverse

User = get_user_model()

@pytest.mark.django_db
class TestTenantInvoiceRBAC:
    def setup_method(self):
        self.client = APIClient()
        self.owner = User.objects.create_user(email="owner@test.com", password="pass")
        self.manager = User.objects.create_user(email="manager@test.com", password="pass")
        self.viewer = User.objects.create_user(email="viewer@test.com", password="pass")

        # ✅ Ensure tier exists
        tier = Tier.objects.get_or_create(name="Free", defaults={"price": 0, "max_users": 10, "max_locations": 5})[0]
        self.tenant = Tenant.objects.create(name="TestTenant", tier=tier)

        TenantUser.objects.create(tenant=self.tenant, user=self.owner, role="owner")
        TenantUser.objects.create(tenant=self.tenant, user=self.manager, role="manager")
        TenantUser.objects.create(tenant=self.tenant, user=self.viewer, role="viewer")  # ✅ align role name

        self.customer = TenantCustomer.objects.create(
            tenant=self.tenant, name="Customer A", email="customer@example.com"
        )

        self.invoice = TenantInvoice.objects.create(
            tenant=self.tenant,
            customer=self.customer,
            amount=100,
            currency="USD",
            due_date=date.today(),
            status="unpaid",
            description="Existing test invoice"   # ✅ added
        )

    
    def test_owner_can_create_invoice(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse("v1:tenantinvoice-list")
        response = self.client.post(url, {
            "customer": self.customer.id,
            "amount": 200,
            "currency": "USD",
            "due_date": str(date.today()),
            "description": "Test invoice for customer A"
        }, format="json")
        print("DEBUG response:", response.data)   # 👈 add this temporarily
        assert response.status_code == 201

    def test_viewer_is_read_only(self):   # 👈 must be indented inside class
        self.client.force_authenticate(user=self.viewer)
        url = reverse("v1:tenantinvoice-list")
        response = self.client.get(url)
        assert response.status_code == 200
        response = self.client.post(url, {
            "customer": self.customer.id,
            "amount": 300,
            "currency": "USD",
            "due_date": str(date.today()),
            "description": "Viewer should not be able to create invoice"
        }, format="json")
        print("DEBUG response:", response.data)   # 👈 add this temporarily
        assert response.status_code == 403


    def test_manager_can_view_but_not_delete_invoice(self):
        self.client.force_authenticate(user=self.manager)
        url = reverse("v1:tenantinvoice-list")
        response = self.client.get(url)
        assert response.status_code == 200
        url_detail = reverse("v1:tenantinvoice-detail", args=[self.invoice.id])
        response = self.client.delete(url_detail)
        assert response.status_code == 403

    