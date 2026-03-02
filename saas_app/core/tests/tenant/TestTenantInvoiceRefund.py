import pytest
from django.utils import timezone
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from saas_app.core.models import TenantInvoice, Tenant, TenantUser

User = get_user_model()


@pytest.mark.django_db
class TestTenantInvoiceRefund:
    def setup_method(self):
        self.client = APIClient()
        # Create a real CustomUser and Tenant
        custom_user = User.objects.create_user(email="tenantuser1@example.com", password="pass123")
        tenant = Tenant.objects.create(email=custom_user.email)
        self.user = TenantUser.objects.create(user=custom_user, tenant=tenant, role="admin")
        self.client.force_authenticate(user=self.user.user)

    def test_refund_paid_invoice(self):
        invoice = TenantInvoice.objects.create(
            tenant=self.user.tenant,
            status="paid",
            amount=100,
            currency="USD",
            due_date=timezone.now().date(),
        )
        response = self.client.patch(f"/api/tenant-invoices/{invoice.id}/mark_refunded/")
        invoice.refresh_from_db()

        assert response.status_code == 200
        assert invoice.status == "refunded"
        assert invoice.refunded_at is not None

    def test_refund_unpaid_invoice_fails(self):
        invoice = TenantInvoice.objects.create(
            tenant=self.user.tenant,
            status="unpaid",
            amount=150,
            currency="USD",
            due_date=timezone.now().date(),
        )
        response = self.client.patch(f"/api/tenant-invoices/{invoice.id}/mark_refunded/")
        invoice.refresh_from_db()

        assert response.status_code == 400
        assert invoice.status == "unpaid"

    def test_refund_overdue_invoice_fails(self):
        invoice = TenantInvoice.objects.create(
            tenant=self.user.tenant,
            status="overdue",
            amount=180,
            currency="USD",
            due_date=timezone.now().date(),
        )
        response = self.client.patch(f"/api/tenant-invoices/{invoice.id}/mark_refunded/")
        invoice.refresh_from_db()

        assert response.status_code == 400
        assert invoice.status == "overdue"
