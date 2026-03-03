from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from datetime import date, timedelta
from rest_framework.test import APITestCase
from saas_app.core.models import PlatformUser, PlatformCustomer, PlatformInvoice, Tenant, Tier, TenantUser

User = get_user_model()


class TestPlatformInvoiceRBAC(APITestCase):

    @classmethod
    def setUpTestData(cls):
        # Create platform users with roles
        cls.platform_admin = User.objects.create_user(email="platform_admin@example.com", password="test123")
        PlatformUser.objects.create(user=cls.platform_admin, role="platform_admin")

        cls.platform_manager = User.objects.create_user(email="platform_manager@example.com", password="test123")
        PlatformUser.objects.create(user=cls.platform_manager, role="platform_manager")

        cls.platform_owner = User.objects.create_user(email="platform_owner@example.com", password="test123")
        PlatformUser.objects.create(user=cls.platform_owner, role="platform_owner")

        cls.platform_user = User.objects.create_user(email="platform_user@example.com", password="test123")
        PlatformUser.objects.create(user=cls.platform_user, role="platform_user")

        cls.platform_viewer = User.objects.create_user(email="platform_viewer@example.com", password="test123")
        PlatformUser.objects.create(user=cls.platform_viewer, role="platform_viewer")

        # Create tenant and tier
        cls.tier = Tier.objects.first() or Tier.objects.create(name="Basic", price=0)
        cls.tenant = Tenant.objects.create(name="Test Tenant", tier=cls.tier, email="tenant@example.com", status="active")

        # Create customer (⚠️ no tenant field here)
        cls.customer = PlatformCustomer.objects.create(name="Test Customer", email="customer@example.com")

        # Link users to tenant
        TenantUser.objects.create(user=cls.platform_admin, tenant=cls.tenant, role="admin")
        TenantUser.objects.create(user=cls.platform_manager, tenant=cls.tenant, role="manager")
        TenantUser.objects.create(user=cls.platform_owner, tenant=cls.tenant, role="owner")
        TenantUser.objects.create(user=cls.platform_user, tenant=cls.tenant, role="user")
        TenantUser.objects.create(user=cls.platform_viewer, tenant=cls.tenant, role="viewer")

        # Create invoice with a safe future due date
        future_date = (date.today() + timedelta(days=7)).isoformat()
        cls.invoice = PlatformInvoice.objects.create(
            tenant=cls.tenant,
            customer=cls.customer,
            amount=Decimal("999.00"),
            currency="USD",
            due_date=future_date,
            status="pending",
            platform_name="Test Platform"
        )

    def test_platform_owner_full_control(self):
        self.client.force_authenticate(user=self.platform_owner)
        url = reverse("v1:platforminvoice-list")
        future_date = (date.today() + timedelta(days=7)).isoformat()
        response = self.client.post(
            url,
            {
                "tenant": self.tenant.id,
                "customer": self.customer.id,
                "amount": "200.00",   # ✅ decimal string
                "currency": "USD",
                "due_date": future_date,   # ✅ always in the future
                "status": "unpaid",
                "description": "Test invoice"
            },
            format="json"
        )
        print("Response data:", response.data)  # debug serializer errors
        self.assertEqual(response.status_code, 201)

    def test_platform_invoice_rbac_matrix(self):
        cases = [
            ("platform_admin", "list", 200),
            ("platform_admin", "create", 403),
            ("platform_admin", "update", 403),
            ("platform_admin", "delete", 403),
            ("platform_admin", "mark_paid", 403),

            ("platform_manager", "list", 200),
            ("platform_manager", "create", 403),
            ("platform_manager", "update", 200),
            ("platform_manager", "delete", 403),
            ("platform_manager", "mark_paid", 200),

            ("platform_user", "list", 200),
            ("platform_user", "create", 201),
            ("platform_user", "update", 403),
            ("platform_user", "delete", 403),
            ("platform_user", "mark_paid", 403),

            ("platform_viewer", "list", 200),
            ("platform_viewer", "create", 403),
            ("platform_viewer", "update", 403),
            ("platform_viewer", "delete", 403),
            ("platform_viewer", "mark_paid", 403),
        ]

        future_date = (date.today() + timedelta(days=7)).isoformat()

        action_map = {
            "list": lambda: self.client.get(reverse("v1:platforminvoice-list")),
            "create": lambda: self.client.post(
                reverse("v1:platforminvoice-list"),
                {
                    "tenant": self.tenant.id,
                    "customer": self.customer.id,
                    "amount": "200.00",
                    "currency": "USD",
                    "due_date": future_date,   # ✅ always in the future
                    "status": "unpaid",
                    "description": "Matrix test"
                },
                format="json"
            ),
            "update": lambda: self.client.patch(
                reverse("v1:platforminvoice-detail", args=[self.invoice.id]),
                {"status": "paid"},
                format="json"
            ),
            "delete": lambda: self.client.delete(
                reverse("v1:platforminvoice-detail", args=[self.invoice.id])
            ),
            "mark_paid": lambda: self.client.patch(
                reverse("v1:platforminvoice-mark-paid", args=[self.invoice.id]),
                {"status": "paid"},
                format="json"
            ),
        }

        for user_attr, action, expected_status in cases:
            with self.subTest(user=user_attr, action=action):
                user = getattr(self, user_attr)
                self.client.force_authenticate(user=user)
                response = action_map[action]()
                print(f"{user_attr} {action} response:", response.data)
                self.assertEqual(response.status_code, expected_status)
