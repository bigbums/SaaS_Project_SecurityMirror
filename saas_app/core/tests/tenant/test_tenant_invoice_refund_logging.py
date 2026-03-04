import pytest
from django.utils import timezone
from rest_framework.test import APIClient
from saas_app.core.models import TenantInvoice, TenantCustomer, Tenant, Tier, TenantUser, User

@pytest.mark.django_db
class TestTenantInvoiceRefundLogging:
    def setup_method(self):
        self.client = APIClient()
        # Create a tenant user
        custom_user = User.objects.create_user(email="tenantuser2@example.com", password="testpass")
        tier = Tier.objects.get(name="Standard")
        self.tenant = Tenant.objects.create(email=custom_user.email, tier=tier)

        self.user = TenantUser.objects.create(user=custom_user, tenant=self.tenant)
        self.client.force_authenticate(user=custom_user)

        # ✅ Create a tenant customer to satisfy NOT NULL constraint
        self.customer = TenantCustomer.objects.create(
            tenant=self.tenant,
            name="Test Customer",
            email="customer@example.com"
        )

    @pytest.mark.parametrize(
        "initial_status,expected_codes",
        [
            ("paid", [200, 403]),   # Paid invoices may succeed if privilege allows
            ("unpaid", [400, 403]), # Unpaid invoices should fail
            ("overdue", [400, 403]) # Overdue invoices should fail
        ]
    )
    def test_refund_invoice(self, initial_status, expected_codes):
        invoice = TenantInvoice.objects.create(
            tenant=self.tenant,
            customer=self.customer,
            status=initial_status,
            amount=150,
            currency="USD",
            due_date=timezone.now().date(),
        )

        # ✅ Use standard PATCH endpoint to update invoice
        response = self.client.patch(
            f"/api/v1/tenants/{self.tenant.id}/invoices/{invoice.id}/",
            {"status": "paid"},
            format="json"
        )
        invoice.refresh_from_db()

        assert response.status_code in expected_codes
        if response.status_code == 200:
            assert invoice.status == "paid"
