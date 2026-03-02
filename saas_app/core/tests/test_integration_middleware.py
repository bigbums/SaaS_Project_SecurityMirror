from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from saas_app.core.middleware.rbac_middleware import RBACMiddleware
from saas_app.core.middleware.TenantMiddleware import TenantMiddleware
from saas_app.core.models import Tenant, TenantUser, Tier, PlatformUser

User = get_user_model()

class MiddlewareIntegrationTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.rbac = RBACMiddleware(lambda req: req)
        self.tenant_mw = TenantMiddleware(lambda req: req)

        # ✅ Fetch or create Free tier safely
        self.tier, _ = Tier.objects.get_or_create(
            name="Free",
            defaults={"max_users": 3, "max_locations": 1, "price": 0}
        )

        # Create a tenant linked to Free tier
        self.tenant = Tenant.objects.create(
            name="IntegrationTenant",
            tier=self.tier,
            status="active"
        )

    def make_user_with_tenant(self, email, role="manager"):
        user = User.objects.create_user(email=email, password="testpass123")
        TenantUser.objects.create(user=user, tenant=self.tenant, role=role)
        tenant_user = TenantUser.objects.create(user=user, tenant=self.tenant, role=role) 
        setattr(user, "role", tenant_user.role) # ✅ attach role
        return user

    def test_authenticated_tenant_user_permissions_and_tenant(self):
        user = self.make_user_with_tenant("tenant_user@example.com", role="manager")
        request = self.factory.get("/dummy-url")
        request.user = user

        # Pass through both middlewares
        self.rbac(request)
        self.tenant_mw(request)

        # Check tenant attached
        self.assertIsNotNone(request.tenant)
        self.assertEqual(request.tenant.name, "IntegrationTenant")

        # Check permissions attached
        self.assertTrue(hasattr(request.user, "permissions"))
        self.assertIn("invoices:view", request.user.permissions)
        self.assertIn("customers:view", request.user.permissions)

    def test_anonymous_user_has_no_tenant_or_permissions(self):
        request = self.factory.get("/dummy-url")
        request.user = AnonymousUser()

        self.rbac(request)
        self.tenant_mw(request)

        self.assertIsNone(request.tenant)
        self.assertFalse(hasattr(request.user, "permissions"))

def test_platform_user_permissions_without_tenant(self):
    user = User.objects.create_user(email="platform_user@example.com", password="testpass123")
    PlatformUser.objects.create(user=user, role="platform_admin")

    request = self.factory.get("/dummy-url")
    request.user = user

    self.rbac(request)
    self.tenant_mw(request)

    # Platform users should not have a tenant
    self.assertIsNone(request.tenant)

    # But they should have permissions
    self.assertTrue(hasattr(request.user, "permissions"))
    self.assertIn("tenants:view", request.user.permissions)  # example permission
