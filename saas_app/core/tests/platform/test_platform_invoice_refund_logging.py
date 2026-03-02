import pytest
from django.utils import timezone
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from saas_app.core.models import PlatformInvoice, PlatformUser
from saas_app.audit.models import AuditTrail

User = get_user_model()


@pytest.mark.django_db
class TestPlatformInvoiceRefundLogging:
    def setup_method(self):
        self.client = APIClient()
        custom_user = User.objects.create_user(email="platformuser2@example.com", password="pass123")
        self.user = PlatformUser.objects.create(user=custom_user)
        self.client.force_authenticate(user=self.user.user)

    def test_platform_refund_logs_audit_entry_with_refunded_at(self):
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

        log_entry = AuditTrail.objects.filter(
            object_id=invoice.id,
            action="platform_invoice_marked_refunded"
        ).first()

        assert log_entry is not None
        assert log_entry.user == self.user.user
        assert "refunded_at" in log_entry.details
        assert log_entry.details["refunded_at"] == invoice.refunded_at.isoformat()


@pytest.mark.django_db
class TestPlatformInvoiceRefundLoggingNegative:
    def setup_method(self):
        self.client = APIClient()
        custom_user = User.objects.create_user(email="platformuser4@example.com", password="pass123")
        self.user = PlatformUser.objects.create(user=custom_user)
        self.client.force_authenticate(user=self.user.user)

    def test_unpaid_platform_invoice_refund_does_not_log_refunded_at(self):
        invoice = PlatformInvoice.objects.create(
            status="unpaid",
            amount=250,
            currency="USD",
            due_date=timezone.now().date(),
        )

        response = self.client.patch(f"/api/platform-invoices/{invoice.id}/mark_refunded/")
        invoice.refresh_from_db()

        assert response.status_code == 400
        assert invoice.status == "unpaid"

        log_entry = AuditTrail.objects.filter(
            object_id=invoice.id,
            action="platform_invoice_marked_refunded"
        ).first()

        if log_entry:
            assert "refunded_at" not in log_entry.details


@pytest.mark.django_db
class TestPlatformInvoiceRefundLoggingOverdue:
    def setup_method(self):
        self.client = APIClient()
        custom_user = User.objects.create_user(email="platformuser6@example.com", password="pass123")
        self.user = PlatformUser.objects.create(user=custom_user)
        self.client.force_authenticate(user=self.user.user)

    def test_overdue_platform_invoice_refund_does_not_log_refunded_at(self):
        invoice = PlatformInvoice.objects.create(
            status="overdue",
            amount=300,
            currency="USD",
            due_date=timezone.now().date(),
        )

        response = self.client.patch(f"/api/platform-invoices/{invoice.id}/mark_refunded/")
        invoice.refresh_from_db()

        assert response.status_code == 400
        assert invoice.status == "overdue"

        log_entry = AuditTrail.objects.filter(
            object_id=invoice.id,
            action="platform_invoice_marked_refunded"
        ).first()

        if log_entry:
            assert "refunded_at" not in log_entry.details


@pytest.mark.django_db
class TestPlatformInvoiceRefundLoggingPositive:
    def setup_method(self):
        self.client = APIClient()
        custom_user = User.objects.create_user(email="platformuser8@example.com", password="pass123")
        self.user = PlatformUser.objects.create(user=custom_user)
        self.client.force_authenticate(user=self.user.user)

    def test_paid_platform_invoice_refund_logs_refunded_at(self):
        invoice = PlatformInvoice.objects.create(
            status="paid",
            amount=220,
            currency="USD",
            due_date=timezone.now().date(),
        )

        response = self.client.patch(f"/api/platform-invoices/{invoice.id}/mark_refunded/")
        invoice.refresh_from_db()

        assert response.status_code == 200
        assert invoice.status == "refunded"
        assert invoice.refunded_at is not None

        log_entry = AuditTrail.objects.filter(
            object_id=invoice.id,
            action="platform_invoice_marked_refunded"
        ).first()

        assert log_entry is not None
        assert "refunded_at" in log_entry.details
        assert log_entry.details["refunded_at"] == invoice.refunded_at.isoformat()
