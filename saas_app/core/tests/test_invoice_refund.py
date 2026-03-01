# tests/test_invoice_refund.py
import pytest
from django.utils import timezone
from rest_framework.test import APIClient
from saas_app.core.models import TenantInvoice, TenantUser
from saas_app.core.constants import INVOICE_STATUS_CHOICES

@pytest.mark.django_db
class TestTenantInvoiceRefund:
    def setup_method(self):
        self.client = APIClient()
        # Create a test user and tenant
        self.user = TenantUser.objects.create(user_id=1, tenant_id=1)
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

    def test_refund_unpaid_invoice_fails(self):
        invoice = TenantInvoice.objects.create(
            tenant=self.user.tenant,
            status="unpaid",
            amount=100,
            currency="USD",
            due_date=timezone.now().date(),
        )
        response = self.client.patch(f"/api/tenant-invoices/{invoice.id}/mark_refunded/")
        invoice.refresh_from_db()

        assert response.status_code == 400
        assert invoice.status == "unpaid"

    def test_refund_invalid_status_choice(self):
        # Temporarily simulate missing 'refunded' in INVOICE_STATUS_CHOICES
        assert "refunded" in [c[0] for c in INVOICE_STATUS_CHOICES]
