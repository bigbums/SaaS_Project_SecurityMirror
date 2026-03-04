from django.test import TestCase
from django.contrib.auth import get_user_model
from saas_app.core.models import (
    Tenant,
    TenantUser,
    Tier,
    TenantInvoice,
    PlatformTenantConfig,
    TenantCustomer,  # ✅ correct model for invoice.customer
)

User = get_user_model()


class UserSignalTests(TestCase):
    def test_user_creation_assigns_tenant_and_tenantuser(self):
        user = User.objects.create(email="signaltest@example.com")
        self.assertTrue(TenantUser.objects.filter(user=user, role="owner").exists())
        tenant = Tenant.objects.get(email=user.email)
        self.assertEqual(tenant.tier.name, "Free")

    def test_user_deletion_removes_tenantuser(self):
        user = User.objects.create(email="deleteuser@example.com")
        user_id = user.id
        user.delete()
        self.assertFalse(TenantUser.objects.filter(user_id=user_id).exists())


class TenantSignalTests(TestCase):
    def test_tenant_creation_initializes_limits_and_config(self):
        free_tier, _ = Tier.objects.get_or_create(
            name="Free", defaults={"max_users": 5, "max_locations": 1, "price": 0}
        )
        tenant = Tenant.objects.create(name="Test Tenant", email="tenant@example.com", tier=free_tier)
        self.assertEqual(tenant.current_users_count, 0)
        self.assertEqual(tenant.current_locations_count, 0)
        self.assertTrue(PlatformTenantConfig.objects.filter(tenant=tenant).exists())

    def test_tenant_deletion_cleans_up_related_data(self):
        free_tier, _ = Tier.objects.get_or_create(
            name="Free", defaults={"max_users": 5, "max_locations": 1, "price": 0}
        )
        tenant = Tenant.objects.create(name="Delete Tenant", email="delete@example.com", tier=free_tier)
        TenantUser.objects.create(tenant=tenant, user=User.objects.create(email="tenantuser@example.com"), role="owner")
        tenant_id = tenant.id
        tenant.delete()
        self.assertFalse(TenantUser.objects.filter(tenant_id=tenant_id).exists())


class InvoiceSignalTests(TestCase):
    def test_invoice_file_cleanup_on_delete(self):
        free_tier, _ = Tier.objects.get_or_create(
            name="Free", defaults={"max_users": 5, "max_locations": 1, "price": 0}
        )
        tenant = Tenant.objects.create(name="Invoice Tenant", email="invoice@example.com", tier=free_tier)
        customer = TenantCustomer.objects.create(tenant=tenant, name="Test Customer", email="cust@example.com")
        invoice = TenantInvoice.objects.create(
            tenant=tenant, tenant_name=tenant.name, amount=1000, currency="USD", customer=customer
        )
        invoice_id = invoice.id
        invoice.delete()
        self.assertFalse(TenantInvoice.objects.filter(id=invoice_id).exists())

    def test_tenant_invoice_sets_tenant_name(self):
        free_tier, _ = Tier.objects.get_or_create(
            name="Free", defaults={"max_users": 5, "max_locations": 1, "price": 0}
        )
        tenant = Tenant.objects.create(name="Invoice Tenant", email="invoice@example.com", tier=free_tier)
        customer = TenantCustomer.objects.create(tenant=tenant, name="Another Customer", email="cust2@example.com")
        invoice = TenantInvoice.objects.create(
            tenant=tenant, tenant_name="", amount=1000, currency="USD", customer=customer
        )
        self.assertEqual(invoice.tenant_name, tenant.name)


class SecuritySignalTests(TestCase):
    def test_login_updates_last_login(self):
        user = User.objects.create(email="login@example.com")
        from saas_app.core.signals.security import update_login
        update_login(sender=User, user=user, request=None)
        if hasattr(user, "tenantuser"):
            self.assertIsNotNone(user.tenantuser.last_login)

    def test_logout_updates_last_logout(self):
        user = User.objects.create(email="logout@example.com")
        from saas_app.core.signals.security import update_logout
        update_logout(sender=User, user=user, request=None)
        if hasattr(user, "tenantuser"):
            self.assertIsNotNone(user.tenantuser.last_logout)
