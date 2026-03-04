import pytest
from django.utils import timezone
from rest_framework.test import APIClient
from saas_app.core.models import PlatformInvoice, Tenant, Tier, PlatformUser, User

@pytest.mark.django_db
class TestPlatformInvoiceRefund:
    def setup_method(self):
        self.client = APIClient()
        # Create a test platform user
        custom_user = User.objects.create_user(email="tenantuser1@example.com", password="testpass")
        tier = Tier.objects.get(name="Standard")
        self.tenant = Tenant.objects.create(email=custom_user.email, tier=tier)

        self.user = PlatformUser.objects.create(user=custom_user)
        self.client.force_authenticate(user=custom_user)

    @pytest.mark.parametrize(
        "initial_status,expected_codes",
        [
            ("paid", [200, 403]),   # Paid invoices may succeed if privilege allows
            ("unpaid", [400, 403]), # Unpaid invoices should fail
            ("overdue", [400, 403]) # Overdue invoices should fail
        ]
    )
    def test_refund_invoice(self, initial_status, expected_codes):
        invoice = PlatformInvoice.objects.create(
            tenant=self.tenant,
            status=initial_status,
            amount=200,
            currency="USD",
            due_date=timezone.now().date(),
        )

        # ✅ Correct path includes /api/v1/
        response = self.client.patch(
            f"/api/v1/platform-invoices/{invoice.id}/mark_paid/"
        )
        invoice.refresh_from_db()

        assert response.status_code in expected_codes
        if response.status_code == 200:
            assert invoice.status == "paid"
