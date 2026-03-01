import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from saas_app.core.models import PlatformInvoice, PlatformUser, Tenant, Tier
from datetime import date
from django.urls import reverse

User = get_user_model()

@pytest.mark.django_db
class TestPlatformInvoiceRBAC:
    def setup_method(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(email="admin@test.com", password="pass")
        self.viewer = User.objects.create_user(email="viewer@test.com", password="pass")

        # ✅ Use platform roles consistent with ROLE_PRIVILEGES
        PlatformUser.objects.create(user=self.admin, role="platform_admin")
        PlatformUser.objects.create(user=self.viewer, role="platform_user")

        tier = Tier.objects.get(name="Free")
        self.tenant = Tenant.objects.create(name="PlatformTenant", tier=tier)

        # ✅ Add description when creating invoice
        self.invoice = PlatformInvoice.objects.create(
            tenant=self.tenant,
            amount=500,
            currency="USD",
            due_date=date.today(),
            status="unpaid",
            description="Test platform invoice for RBAC"   # ✅ added
        )

    def test_admin_can_mark_paid(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("v1:platforminvoice-mark-paid", args=[self.invoice.id])
        response = self.client.patch(url)
        assert response.status_code == 200
        assert response.data["success"] is True

    def test_viewer_cannot_mark_paid(self):
        self.client.force_authenticate(user=self.viewer)
        url = reverse("v1:platforminvoice-mark-paid", args=[self.invoice.id])
        response = self.client.patch(url)
        assert response.status_code == 403
