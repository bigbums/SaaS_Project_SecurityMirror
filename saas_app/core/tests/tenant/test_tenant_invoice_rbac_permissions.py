from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from saas_app.core.models import TenantUser, TenantCustomer, TenantInvoice, Tenant, Tier
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class TestTenantInvoiceRBAC(APITestCase):

    @classmethod
    def setUpTestData(cls):
        # Create tenant roles (users)
        cls.tenant_admin = User.objects.create_user(email="tenant_admin@example.com", password="test123")
        cls.tenant_manager = User.objects.create_user(email="tenant_manager@example.com", password="test123")
        cls.tenant_owner = User.objects.create_user(email="tenant_owner@example.com", password="test123")
        cls.tenant_user = User.objects.create_user(email="tenant_user@example.com", password="test123")
        cls.tenant_viewer = User.objects.create_user(email="tenant_viewer@example.com", password="test123")

        # Tenant setup
        cls.tier = Tier.objects.first() or Tier.objects.create(name="Basic", price=0)
        cls.tenant = Tenant.objects.create(
            name="Tenant RBAC Test",
            tier=cls.tier,
            email="tenant_rbac@example.com",
            status="active"
        )

        # Link users to tenant
        TenantUser.objects.create(user=cls.tenant_admin, tenant=cls.tenant, role="admin")
        TenantUser.objects.create(user=cls.tenant_manager, tenant=cls.tenant, role="manager")
        TenantUser.objects.create(user=cls.tenant_owner, tenant=cls.tenant, role="owner")
        TenantUser.objects.create(user=cls.tenant_user, tenant=cls.tenant, role="user")
        TenantUser.objects.create(user=cls.tenant_viewer, tenant=cls.tenant, role="viewer")

        # ✅ Create a tenant customer
        cls.customer = TenantCustomer.objects.create(
            tenant=cls.tenant,
            name="Test Customer",
            email="customer@example.com"
        )

        # ✅ Create invoice attached to tenant + customer with safe future due date
        future_date = (timezone.now().date() + timedelta(days=1)).isoformat()
        cls.invoice = TenantInvoice.objects.create(
            tenant=cls.tenant,
            customer=cls.customer,
            amount=500,
            currency="USD",
            due_date=future_date,
            status="unpaid",
            description="Tenant test invoice"
        )

    def test_tenant_owner_full_control(self):
        self.client.force_authenticate(user=self.tenant_owner)
        url = reverse("v1:tenantinvoice-list", kwargs={"tenant_id": self.tenant.id})
        response = self.client.post(
            url,
            {
                "tenant": self.tenant.id,
                "customer": self.customer.id,
                "amount": 100,
                "currency": "USD",
                "due_date": (timezone.now().date() + timedelta(days=1)).isoformat(),
                "status": "unpaid",
                "description": "Owner test invoice"
            },
            format="json"
        )
        self.assertEqual(response.status_code, 201)
        invoice_id = response.data["id"]

        response = self.client.patch(
            reverse("v1:tenantinvoice-detail", kwargs={"tenant_id": self.tenant.id, "pk": invoice_id}),
            {"status": "paid"},
            format="json"
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.delete(
            reverse("v1:tenantinvoice-detail", kwargs={"tenant_id": self.tenant.id, "pk": invoice_id})
        )
        self.assertEqual(response.status_code, 204)

    def test_tenant_invoice_rbac_matrix(self):
        cases = [
            ("tenant_admin", "list", 200),
            ("tenant_admin", "create", 403),
            ("tenant_admin", "update", 403),
            ("tenant_admin", "delete", 403),

            ("tenant_manager", "list", 200),
            ("tenant_manager", "create", 403),
            ("tenant_manager", "update", 200),
            ("tenant_manager", "delete", 403),

            ("tenant_user", "list", 200),
            ("tenant_user", "create", 201),
            ("tenant_user", "update", 403),
            ("tenant_user", "delete", 403),

            ("tenant_viewer", "list", 200),
            ("tenant_viewer", "create", 403),
            ("tenant_viewer", "update", 403),
            ("tenant_viewer", "delete", 403),
        ]

        action_map = {
            "list": lambda: self.client.get(reverse("v1:tenantinvoice-list", kwargs={"tenant_id": self.tenant.id})),
            "create": lambda: self.client.post(
                reverse("v1:tenantinvoice-list", kwargs={"tenant_id": self.tenant.id}),
                {
                    "tenant": self.tenant.id,
                    "customer": self.customer.id,
                    "amount": 200,
                    "currency": "USD",
                    "due_date": (timezone.now().date() + timedelta(days=1)).isoformat(),
                    "status": "unpaid",
                    "description": "Matrix test"
                },
                format="json"
            ),
            "update": lambda: self.client.patch(
                reverse("v1:tenantinvoice-detail", kwargs={"tenant_id": self.tenant.id, "pk": self.invoice.id}),
                {"status": "paid"},
                format="json"
            ),
            "delete": lambda: self.client.delete(
                reverse("v1:tenantinvoice-detail", kwargs={"tenant_id": self.tenant.id, "pk": self.invoice.id})
            ),
        }

        for user_attr, action, expected_status in cases:
            with self.subTest(user=user_attr, action=action):
                user = getattr(self, user_attr)
                self.client.force_authenticate(user=user)
                response = action_map[action]()
                self.assertEqual(response.status_code, expected_status)
