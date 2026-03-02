from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from saas_app.core.middleware.rbac_middleware import RBACMiddleware
from saas_app.core.middleware.TenantMiddleware import TenantMiddleware
from saas_app.core.models import PlatformUser

User = get_user_model()

class PlatformRolesIntegrationTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.rbac = RBACMiddleware(lambda req: req)
        self.tenant_mw = TenantMiddleware(lambda req: req)

    def make_platform_user(self, email, role):
        user = User.objects.create_user(email=email, password="testpass123")
        PlatformUser.objects.create(user=user, role=role)
        return user

    def test_platform_owner_permissions(self):
        user = self.make_platform_user("owner@example.com", "platform_owner")
        request = self.factory.get("/dummy-url")
        request.user = user

        self.rbac(request)
        self.tenant_mw(request)

        self.assertIsNone(request.tenant)
        self.assertIn("tenants:create", request.user.permissions)
        self.assertIn("platform_users:manage", request.user.permissions)

    def test_platform_admin_permissions(self):
        user = self.make_platform_user("admin@example.com", "platform_admin")
        request = self.factory.get("/dummy-url")
        request.user = user

        self.rbac(request)
        self.tenant_mw(request)

        self.assertIsNone(request.tenant)
        self.assertIn("tenants:view", request.user.permissions)
        self.assertIn("platform_users:manage", request.user.permissions)

    def test_platform_manager_permissions(self):
        user = self.make_platform_user("manager@example.com", "platform_manager")
        request = self.factory.get("/dummy-url")
        request.user = user

        self.rbac(request)
        self.tenant_mw(request)

        self.assertIsNone(request.tenant)
        self.assertIn("tenants:view", request.user.permissions)
        self.assertIn("reports:view", request.user.permissions)

    def test_platform_user_permissions(self):
        user = self.make_platform_user("user@example.com", "platform_user")
        request = self.factory.get("/dummy-url")
        request.user = user

        self.rbac(request)
        self.tenant_mw(request)

        self.assertIsNone(request.tenant)
        self.assertIn("tenants:view", request.user.permissions)
