from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from django.urls import reverse
from saas_app.core.models import (
    Tenant, Tier, TenantUser,
    PlatformUser, PlatformCustomer,
    TenantCustomer, Currency
)
from saas_app.core.constants import VALID_CURRENCIES
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class BaseInvoiceTestCase(APITestCase):
    """Shared setup for invoice-related tests."""

    @classmethod
    def setUpTestData(cls):
        # 🔑 Seed currencies once for all tests
        for code in VALID_CURRENCIES:
            Currency.objects.get_or_create(
                code=code,
                defaults={"name": code, "active": True}
            )


class BaseTenantTestCase(BaseInvoiceTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # Tenant + tier
        cls.tier = Tier.objects.first() or Tier.objects.create(name="Basic", price=0)
        cls.tenant = Tenant.objects.create(
            name="Test Tenant",
            tier=cls.tier,
            email="tenant@example.com",
            status="active"
        )

        # Users + roles
        cls.tenant_owner = User.objects.create_user(email="owner@example.com", password="test123")
        cls.tenant_admin = User.objects.create_user(email="admin@example.com", password="test123")
        cls.tenant_manager = User.objects.create_user(email="manager@example.com", password="test123")
        cls.tenant_user = User.objects.create_user(email="user@example.com", password="test123")
        cls.tenant_viewer = User.objects.create_user(email="viewer@example.com", password="test123")

        TenantUser.objects.create(user=cls.tenant_owner, tenant=cls.tenant, role="owner")
        TenantUser.objects.create(user=cls.tenant_admin, tenant=cls.tenant, role="admin")
        TenantUser.objects.create(user=cls.tenant_manager, tenant=cls.tenant, role="manager")
        TenantUser.objects.create(user=cls.tenant_user, tenant=cls.tenant, role="user")
        TenantUser.objects.create(user=cls.tenant_viewer, tenant=cls.tenant, role="viewer")

        # Customer
        cls.customer = TenantCustomer.objects.create(
            tenant=cls.tenant,
            name="Tenant Customer",
            email="customer@example.com"
        )

    # 🔑 Helper: create tenant invoice
    def create_invoice(self, user, currency="NGN", amount=200):
        self.client.force_authenticate(user=user)
        url = reverse("v1:tenantinvoice-list", kwargs={"tenant_id": self.tenant.id})
        payload = {
            "customer": self.customer.id,
            "amount": amount,
            "currency": currency,
            "due_date": (timezone.now().date() + timedelta(days=1)).isoformat(),
            "status": "unpaid",
            "description": f"Invoice in {currency}"
        }
        return self.client.post(url, payload, format="json")


class BasePlatformTestCase(BaseInvoiceTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # Seed a tenant (needed for invoices)
        cls.tier = Tier.objects.first() or Tier.objects.create(name="Basic", price=0)
        cls.tenant = Tenant.objects.create(
            name="Platform Tenant",
            tier=cls.tier,
            email="platformtenant@example.com",
            status="active"
        )

        # Platform users + roles
        cls.platform_owner = User.objects.create_user(email="platform_owner@example.com", password="test123")
        cls.platform_admin = User.objects.create_user(email="platform_admin@example.com", password="test123")
        cls.platform_manager = User.objects.create_user(email="platform_manager@example.com", password="test123")
        cls.platform_user = User.objects.create_user(email="platform_user@example.com", password="test123")
        cls.platform_viewer = User.objects.create_user(email="platform_viewer@example.com", password="test123")

        PlatformUser.objects.create(user=cls.platform_owner, role="platform_owner")
        PlatformUser.objects.create(user=cls.platform_admin, role="platform_admin")
        PlatformUser.objects.create(user=cls.platform_manager, role="platform_manager")
        PlatformUser.objects.create(user=cls.platform_user, role="platform_user")
        PlatformUser.objects.create(user=cls.platform_viewer, role="platform_viewer")

        # Platform customer
        cls.customer = PlatformCustomer.objects.create(
            name="Platform Customer",
            email="customer@example.com"
        )

    # 🔑 Helper: create platform invoice
    def create_invoice(self, user, currency="NGN", amount=200):
        self.client.force_authenticate(user=user)
        url = reverse("v1:platforminvoice-list")
        payload = {
            "tenant": None,
            "customer": self.customer.id,
            "amount": amount,
            "currency": currency,
            "due_date": (timezone.now().date() + timedelta(days=1)).isoformat(),
            "status": "unpaid",
            "description": f"Platform invoice in {currency}"
        }
        return self.client.post(url, payload, format="json")
