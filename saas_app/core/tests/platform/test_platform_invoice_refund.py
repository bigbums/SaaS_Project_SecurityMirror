# tests/test_platform_invoice_refund.py
import pytest
from django.utils import timezone
from rest_framework.test import APIClient
from saas_app.core.models import PlatformInvoice, PlatformUser

@pytest.mark.django_db
class TestPlatformInvoiceRefund:
    def setup_method(self):
        self.client = APIClient()
        # Create a test platform user
        self.user = PlatformUser.objects.create(user_id=1)
        self.client.force_authenticate(user=self.user.user)

    def test_refund_paid_invoice(self):
        invoice = PlatformInvoice.objects.create(
            status="paid",
            amount=200,
            currency="USD",
            due_date=timezone.now().date(),
        )
        response = self.client.patch(f"/api/platform-invoices/{invoice.id}/mark_refunded/")
        invoice.refresh_from_db()

        assert response.status_code == 200
        assert invoice.status == "refunded"
        assert invoice.refunded_at is not None

    def test_refund_unpaid_invoice_fails(self):
        invoice = PlatformInvoice.objects.create(
            status="unpaid",
            amount=200,
            currency="USD",
            due_date=timezone.now().date(),
        )
        response = self.client.patch(f"/api/platform-invoices/{invoice.id}/mark_refunded/")
        invoice.refresh_from_db()

        assert response.status_code == 400
        assert invoice.status == "unpaid"

    def test_refund_overdue_invoice_fails(self):
        invoice = PlatformInvoice.objects.create(
            status="overdue",
            amount=200,
            currency="USD",
            due_date=timezone.now().date(),
        )
        response = self.client.patch(f"/api/platform-invoices/{invoice.id}/mark_refunded/")
        invoice.refresh_from_db()

        assert response.status_code == 400
        assert invoice.status == "overdue"
