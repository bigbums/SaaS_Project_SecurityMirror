import pytest
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from saas_app.core.middleware.rbac_middleware import RBACMiddleware
from saas_app.core.models import Tenant, TenantUser, Tier, PlatformUser

User = get_user_model()


# ---------------- Tenant Role Tests ----------------
@pytest.mark.tenant
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

        assert "invoice:view" in perms
        assert "tenant:create" in perms
        assert "customer:view" in perms

    def test_manager_permissions(self):
        user = self.make_user("manager@example.com", "manager")
        request = self.factory.get("/dummy-url")
        request.user = user
        request.tenant = self.tenant

        self.middleware(request)
        perms = request.user.permissions

        assert "invoice:view" in perms
        assert "tenant:update" in perms
        assert "customer:view" in perms

    def test_viewer_permissions(self):
        user = self.make_user("viewer@example.com", "viewer")
        request = self.factory.get("/dummy-url")
        request.user = user
        request.tenant = self.tenant

        self.middleware(request)
        perms = request.user.permissions

        assert "invoice:view" in perms
        assert "customer:view" in perms
        assert "tenant:update" not in perms
        assert "tenant:create" not in perms

    # Negative tests
    def test_admin_cannot_update_or_delete_tenant(self):
        user = self.make_user("admin@example.com", "admin")
        request = self.factory.get("/dummy-url")
        request.user = user
        request.tenant = self.tenant

        self.middleware(request)
        perms = request.user.permissions

        assert "tenant:update" not in perms
        assert "tenant:delete" not in perms

    def test_manager_cannot_create_or_delete_tenant(self):
        user = self.make_user("manager@example.com", "manager")
        request = self.factory.get("/dummy-url")
        request.user = user
        request.tenant = self.tenant

        self.middleware(request)
        perms = request.user.permissions

        assert "tenant:create" not in perms
        assert "tenant:delete" not in perms

    def test_viewer_cannot_manage_users_or_billing(self):
        user = self.make_user("viewer@example.com", "viewer")
        request = self.factory.get("/dummy-url")
        request.user = user
        request.tenant = self.tenant

        self.middleware(request)
        perms = request.user.permissions

        assert "user:manage" not in perms
        assert "billing:manage" not in perms


# ---------------- Platform Role Tests ----------------
@pytest.mark.platform
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

        assert "tenant:create" in perms
        assert "tenant:update" in perms
        assert "tenant:delete" in perms
        assert "platform_user:manage" in perms
        assert "platform_setting:update" in perms
        assert "report:view" in perms

    def test_platform_admin_permissions(self):
        user = self.make_user("padmin@example.com", "platform_admin")
        request = self.factory.get("/dummy-url")
        request.user = user

        self.middleware(request)
        perms = request.user.permissions

        assert "tenant:view" in perms
        assert "tenant:update" in perms
        assert "platform_user:manage" in perms
        assert "platform_setting:update" in perms
        assert "report:view" in perms

    def test_platform_manager_permissions(self):
        user = self.make_user("pmanager@example.com", "platform_manager")
        request = self.factory.get("/dummy-url")
        request.user = user

        self.middleware(request)
        perms = request.user.permissions

        assert "tenant:view" in perms
        assert "report:view" in perms
        assert "platform_user:manage" not in perms

    def test_platform_user_permissions(self):
        user = self.make_user("puser@example.com", "platform_user")
        request = self.factory.get("/dummy-url")
        request.user = user

        self.middleware(request)
        perms = request.user.permissions

        assert "tenant:view" in perms
        assert "report:view" not in perms
        assert "platform_user:manage" not in perms

    # Negative tests
    def test_platform_admin_cannot_delete_tenant(self):
        user = self.make_user("padmin@example.com", "platform_admin")
        request = self.factory.get("/dummy-url")
        request.user = user

        self.middleware(request)
        perms = request.user.permissions

        assert "tenant:delete" not in perms

    def test_platform_manager_cannot_update_or_delete_tenant(self):
        user = self.make_user("pmanager@example.com", "platform_manager")
        request = self.factory.get("/dummy-url")
        request.user = user

        self.middleware(request)
        perms = request.user.permissions

        assert "tenant:update" not in perms
        assert "tenant:delete" not in perms

    def test_platform_user_cannot_manage_or_report(self):
        user = self.make_user("puser@example.com", "platform_user")
        request = self.factory.get("/dummy-url")
        request.user = user

        self.middleware(request)
        perms = request.user.permissions

        assert "report:view" not in perms
        assert "platform_user:manage" not in perms
        assert "platform_setting:update" not in perms
