from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from saas_app.core.models import (
    Tenant, Tier, TenantCustomer, TenantInvoice,
    PlatformCustomer, PlatformInvoice, TenantUser, PlatformUser
)
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import time

User = get_user_model()


class TestInvoiceEdgeCases(APITestCase):

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

        # Tenant setup
        cls.tier = Tier.objects.first() or Tier.objects.create(name="Basic", price=0)
        cls.tenant = Tenant.objects.create(
            name="Validation Tenant",
            tier=cls.tier,
            email="validation@example.com",
            status="active"
        )

        # Link tenant owner to tenant
        cls.tenant_owner = User.objects.create_user(email="tenant_owner@example.com", password="test123")
        TenantUser.objects.create(user=cls.tenant_owner, tenant=cls.tenant, role="owner")

        # Create tenant customer
        cls.tenant_customer = TenantCustomer.objects.create(
            tenant=cls.tenant,
            name="Tenant Customer",
            email="tenant_customer@example.com"
        )

        # Create platform customer
        cls.platform_customer = PlatformCustomer.objects.create(
            name="Platform Customer",
            email="platform_customer@example.com"
        )

        # Safe future date
        cls.future_date = (timezone.now().date() + timedelta(days=1)).isoformat()

    # ---------------- Tenant Invoice Edge Cases ----------------
    def test_tenant_invoice_negative_amount(self):
        self.client.force_authenticate(user=self.tenant_owner)
        url = reverse("v1:tenantinvoice-list", kwargs={"tenant_id": self.tenant.id})
        response = self.client.post(url, {
            "tenant": self.tenant.id,
            "customer": self.tenant_customer.id,
            "amount": -100,
            "currency": "USD",
            "due_date": self.future_date,
            "status": "unpaid",
            "description": "Negative amount test"
        }, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("amount", response.data)

    def test_tenant_invoice_invalid_currency(self):
        self.client.force_authenticate(user=self.tenant_owner)
        url = reverse("v1:tenantinvoice-list", kwargs={"tenant_id": self.tenant.id})
        response = self.client.post(url, {
            "tenant": self.tenant.id,
            "customer": self.tenant_customer.id,
            "amount": 100,
            "currency": "XYZ",
            "due_date": self.future_date,
            "status": "unpaid",
            "description": "Invalid currency test"
        }, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("currency", response.data)

    def test_tenant_invoice_past_due_date(self):
        self.client.force_authenticate(user=self.tenant_owner)
        url = reverse("v1:tenantinvoice-list", kwargs={"tenant_id": self.tenant.id})
        past_date = (timezone.now().date() - timedelta(days=1)).isoformat()
        response = self.client.post(url, {
            "tenant": self.tenant.id,
            "customer": self.tenant_customer.id,
            "amount": 100,
            "currency": "USD",
            "due_date": past_date,
            "status": "unpaid",
            "description": "Past due date test"
        }, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("due_date", response.data)


    def test_bulk_tenant_invoice_creation(self):
        # Authenticate as tenant_owner who has create permission
        self.client.force_authenticate(user=self.tenant_owner)
        url = reverse("v1:tenantinvoice-list", kwargs={"tenant_id": self.tenant.id})

        invoices = []
        for i in range(50):  # simulate 50 invoices
            invoices.append({
                "tenant": self.tenant.id,
                "customer": self.tenant_customer.id,
                "amount": 100 + i,
                "currency": "USD",
                "due_date": (timezone.now().date() + timedelta(days=7)).isoformat(),
                "status": "unpaid",
                "description": f"Bulk invoice {i}"
            })

        # Send them one by one
        for payload in invoices:
            response = self.client.post(url, payload, format="json")
            self.assertEqual(response.status_code, 201)

   

    def test_bulk_tenant_invoice_creation_performance(self):
        self.client.force_authenticate(user=self.tenant_owner)
        url = reverse("v1:tenantinvoice-list", kwargs={"tenant_id": self.tenant.id})

        invoices = []
        for i in range(50):
            invoices.append({
                "tenant": self.tenant.id,
                "customer": self.tenant_customer.id,
                "amount": 100 + i,
                "currency": "USD",
                "due_date": (timezone.now().date() + timedelta(days=7)).isoformat(),
                "status": "unpaid",
                "description": f"Bulk invoice {i}"
            })

        start_time = time.time()
        for payload in invoices:
            response = self.client.post(url, payload, format="json")
            self.assertEqual(response.status_code, 201)
        end_time = time.time()

        duration = end_time - start_time
        print(f"Created 50 tenant invoices in {duration:.2f} seconds")
        # Optional: enforce a performance threshold
        self.assertLess(duration, 10.0, "Bulk invoice creation took too long")


    # ---------------- Platform Invoice Edge Cases ----------------
    def test_platform_invoice_invalid_tenant_customer_ids(self):
        self.client.force_authenticate(user=self.platform_user)  # ✅ now exists
        url = reverse("v1:platforminvoice-list")
        response = self.client.post(url, {
            "tenant": 9999,
            "customer": 9999,
            "amount": 100,
            "currency": "USD",
            "due_date": self.future_date,
            "status": "unpaid",
            "description": "Invalid tenant/customer test"
        }, format="json")
        self.assertEqual(response.status_code, 400)

    def test_platform_invoice_invalid_status_transition(self):
        self.client.force_authenticate(user=self.platform_manager)  # ✅ now exists
        invoice = PlatformInvoice.objects.create(
            tenant=self.tenant,
            customer=self.platform_customer,
            amount=Decimal("100.00"),
            currency="USD",
            due_date=self.future_date,
            status="unpaid",
            description="Valid invoice"
        )
        url = reverse("v1:platforminvoice-detail", args=[invoice.id])
        response = self.client.patch(url, {"status": "archived"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("status", response.data)

    def test_bulk_platform_invoice_creation(self):
        # Authenticate as platform_owner who has create permission
        self.client.force_authenticate(user=self.platform_owner)
        url = reverse("v1:platforminvoice-list")

        invoices = []
        for i in range(50):  # simulate 50 invoices
            invoices.append({
                "tenant": self.tenant.id,
                "customer": self.platform_customer.id,
                "amount": 200 + i,
                "currency": "USD",
                "due_date": (timezone.now().date() + timedelta(days=7)).isoformat(),
                "status": "unpaid",
                "description": f"Bulk platform invoice {i}"
            })

        # Send them one by one
        for payload in invoices:
            response = self.client.post(url, payload, format="json")
            self.assertEqual(response.status_code, 201)

    def test_bulk_platform_invoice_creation_performance(self):
        self.client.force_authenticate(user=self.platform_owner)
        url = reverse("v1:platforminvoice-list")

        invoices = []
        for i in range(50):
            invoices.append({
                "tenant": self.tenant.id,
                "customer": self.platform_customer.id,
                "amount": 200 + i,
                "currency": "USD",
                "due_date": (timezone.now().date() + timedelta(days=7)).isoformat(),
                "status": "unpaid",
                "description": f"Bulk platform invoice {i}"
            })

        start_time = time.time()
        for payload in invoices:
            response = self.client.post(url, payload, format="json")
            self.assertEqual(response.status_code, 201)
        end_time = time.time()

        duration = end_time - start_time
        print(f"Created 50 platform invoices in {duration:.2f} seconds")
        self.assertLess(duration, 10.0, "Bulk platform invoice creation took too long")

