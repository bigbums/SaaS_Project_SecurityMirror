import pytest
from django.utils import timezone
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from saas_app.core.models import TenantInvoice, TenantUser, Tenant
from saas_app.audit.models import AuditTrail

User = get_user_model()


@pytest.mark.django_db
class TestTenantInvoiceRefundLogging:
    def setup_method(self):
        self.client = APIClient()
        custom_user = User.objects.create_user(email="tenantuser1@example.com", password="pass123")
        tenant = Tenant.objects.create(email=custom_user.email)
        self.user = TenantUser.objects.create(user=custom_user, tenant=tenant, role="admin")
        self.client.force_authenticate(user=self.user.user)

    def test_refund_logs_audit_entry_with_refunded_at(self):
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

        log_entry = AuditTrail.objects.filter(
            object_id=invoice.id,
            action="tenant_invoice_marked_refunded"
        ).first()

        assert log_entry is not None
        assert log_entry.user == self.user.user
        assert "refunded_at" in log_entry.details
        assert log_entry.details["refunded_at"] == invoice.refunded_at.isoformat()


@pytest.mark.django_db
class TestTenantInvoiceRefundLoggingNegative:
    def setup_method(self):
        self.client = APIClient()
        custom_user = User.objects.create_user(email="tenantuser3@example.com", password="pass123")
        tenant = Tenant.objects.create(email=custom_user.email)
        self.user = TenantUser.objects.create(user=custom_user, tenant=tenant, role="admin")
        self.client.force_authenticate(user=self.user.user)

    def test_unpaid_invoice_refund_does_not_log_refunded_at(self):
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

        log_entry = AuditTrail.objects.filter(
            object_id=invoice.id,
            action="tenant_invoice_marked_refunded"
        ).first()

        if log_entry:
            assert "refunded_at" not in log_entry.details


@pytest.mark.django_db
class TestTenantInvoiceRefundLoggingOverdue:
    def setup_method(self):
        self.client = APIClient()
        custom_user = User.objects.create_user(email="tenantuser5@example.com", password="pass123")
        tenant = Tenant.objects.create(email=custom_user.email)
        self.user = TenantUser.objects.create(user=custom_user, tenant=tenant, role="admin")
        self.client.force_authenticate(user=self.user.user)

    def test_overdue_invoice_refund_does_not_log_refunded_at(self):
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

        log_entry = AuditTrail.objects.filter(
            object_id=invoice.id,
            action="tenant_invoice_marked_refunded"
        ).first()

        if log_entry:
            assert "refunded_at" not in log_entry.details


@pytest.mark.django_db
class TestTenantInvoiceRefundLoggingPositive:
    def setup_method(self):
        self.client = APIClient()
        custom_user = User.objects.create_user(email="tenantuser7@example.com", password="pass123")
        tenant = Tenant.objects.create(email=custom_user.email)
        self.user = TenantUser.objects.create(user=custom_user, tenant=tenant, role="admin")
        self.client.force_authenticate(user=self.user.user)

    def test_paid_invoice_refund_logs_refunded_at(self):
        invoice = TenantInvoice.objects.create(
            tenant=self.user.tenant,
            status="paid",
            amount=120,
            currency="USD",
            due_date=timezone.now().date(),
        )

        response = self.client.patch(f"/api/tenant-invoices/{invoice.id}/mark_refunded/")
        invoice.refresh_from_db()

        assert response.status_code == 200
        assert invoice.status == "refunded"
        assert invoice.refunded_at is not None

        log_entry = AuditTrail.objects.filter(
            object_id=invoice.id,
            action="tenant_invoice_marked_refunded"
        ).first()

        assert log_entry is not None
        assert "refunded_at" in log_entry.details
        assert log_entry.details["refunded_at"] == invoice.refunded_at.isoformat()
