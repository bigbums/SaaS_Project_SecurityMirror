from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from saas_app.core.middleware.rbac_middleware import RBACMiddleware
from saas_app.core.models import Tenant, TenantUser, Tier, PlatformUser

User = get_user_model()


# ---------------- Tenant Role Tests ----------------
class TenantRoleTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = RBACMiddleware(lambda req: req)

        # ✅ Use an existing seeded Tier
        self.tier = Tier.objects.first()

        # Create a shared tenant with a valid tier
        self.tenant = Tenant.objects.create(
            name="TestTenant",
            tier=self.tier,
            status="active"
        )

    def make_user(self, email, role):
        user = User.objects.create_user(email=email, password="testpass123")
        TenantUser.objects.create(user=user, tenant=self.tenant, role=role)
        return user

    # Positive tests
    def test_admin_permissions(self):
        user = self.make_user("admin@example.com", "admin")
        request = self.factory.get("/dummy-url")
        request.user = user
        request.tenant = self.tenant

        self.middleware(request)
        perms = request.user.permissions

        self.assertIn("invoice:view", perms)
        self.assertIn("tenant:create", perms)
        self.assertIn("customer:view", perms)

    def test_manager_permissions(self):
        user = self.make_user("manager@example.com", "manager")
        request = self.factory.get("/dummy-url")
        request.user = user
        request.tenant = self.tenant

        self.middleware(request)
        perms = request.user.permissions

        self.assertIn("invoice:view", perms)
        self.assertIn("tenant:update", perms)
        self.assertIn("customer:view", perms)

    def test_viewer_permissions(self):
        user = self.make_user("viewer@example.com", "viewer")
        request = self.factory.get("/dummy-url")
        request.user = user
        request.tenant = self.tenant

        self.middleware(request)
        perms = request.user.permissions

        self.assertIn("invoice:view", perms)
        self.assertIn("customer:view", perms)
        self.assertNotIn("tenant:update", perms)
        self.assertNotIn("tenant:create", perms)

    # Negative tests
    def test_admin_cannot_update_or_delete_tenant(self):
        user = self.make_user("admin@example.com", "admin")
        request = self.factory.get("/dummy-url")
        request.user = user
        request.tenant = self.tenant

        self.middleware(request)
        perms = request.user.permissions

        self.assertNotIn("tenant:update", perms)
        self.assertNotIn("tenant:delete", perms)

    def test_manager_cannot_create_or_delete_tenant(self):
        user = self.make_user("manager@example.com", "manager")
        request = self.factory.get("/dummy-url")
        request.user = user
        request.tenant = self.tenant

        self.middleware(request)
        perms = request.user.permissions

        self.assertNotIn("tenant:create", perms)
        self.assertNotIn("tenant:delete", perms)

    def test_viewer_cannot_manage_users_or_billing(self):
        user = self.make_user("viewer@example.com", "viewer")
        request = self.factory.get("/dummy-url")
        request.user = user
        request.tenant = self.tenant

        self.middleware(request)
        perms = request.user.permissions

        self.assertNotIn("user:manage", perms)
        self.assertNotIn("billing:manage", perms)


# ---------------- Platform Role Tests ----------------
class PlatformRoleTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = RBACMiddleware(lambda req: req)

    def make_user(self, email, role):
        user = User.objects.create_user(email=email, password="testpass123")
        PlatformUser.objects.create(user=user, role=role)
        return user

    # Positive tests
    def test_platform_owner_permissions(self):
        user = self.make_user("powner@example.com", "platform_owner")
        request = self.factory.get("/dummy-url")
        request.user = user

        self.middleware(request)
        perms = request.user.permissions

        self.assertIn("tenant:create", perms)
        self.assertIn("tenant:update", perms)
        self.assertIn("tenant:delete", perms)
        self.assertIn("platform_user:manage", perms)
        self.assertIn("platform_setting:update", perms)
        self.assertIn("report:view", perms)

    def test_platform_admin_permissions(self):
        user = self.make_user("padmin@example.com", "platform_admin")
        request = self.factory.get("/dummy-url")
        request.user = user

        self.middleware(request)
        perms = request.user.permissions

        self.assertIn("tenant:view", perms)
        self.assertIn("tenant:update", perms)
        self.assertIn("platform_user:manage", perms)
        self.assertIn("platform_setting:update", perms)
        self.assertIn("report:view", perms)

    def test_platform_manager_permissions(self):
        user = self.make_user("pmanager@example.com", "platform_manager")
        request = self.factory.get("/dummy-url")
        request.user = user

        self.middleware(request)
        perms = request.user.permissions

        self.assertIn("tenant:view", perms)
        self.assertIn("report:view", perms)
        self.assertNotIn("platform_user:manage", perms)

    def test_platform_user_permissions(self):
        user = self.make_user("puser@example.com", "platform_user")
        request = self.factory.get("/dummy-url")
        request.user = user

        self.middleware(request)
        perms = request.user.permissions

        self.assertIn("tenant:view", perms)
        self.assertNotIn("report:view", perms)
        self.assertNotIn("platform_user:manage", perms)

    # Negative tests
    def test_platform_admin_cannot_delete_tenant(self):
        user = self.make_user("padmin@example.com", "platform_admin")
        request = self.factory.get("/dummy-url")
        request.user = user

        self.middleware(request)
        perms = request.user.permissions

        self.assertNotIn("tenant:delete", perms)

    def test_platform_manager_cannot_update_or_delete_tenant(self):
        user = self.make_user("pmanager@example.com", "platform_manager")
        request = self.factory.get("/dummy-url")
        request.user = user

        self.middleware(request)
        perms = request.user.permissions

        self.assertNotIn("tenant:update", perms)
        self.assertNotIn("tenant:delete", perms)

    def test_platform_user_cannot_manage_or_report(self):
        user = self.make_user("puser@example.com", "platform_user")
        request = self.factory.get("/dummy-url")
        request.user = user

        self.middleware(request)
        perms = request.user.permissions

        self.assertNotIn("report:view", perms)
        self.assertNotIn("platform_user:manage", perms)
        self.assertNotIn("platform_setting:update", perms)
