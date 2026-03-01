from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from saas_app.core.models import Tenant, TenantUser, Tier
from saas_app.core.middleware.rbac_middleware import RBACMiddleware


User = get_user_model()



class TenantRolesIntegrationTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        # ✅ Create a Tier first
        self.tier = Tier.objects.create(
            name="Basic",
            price=0,
            max_users=10,
            max_locations=5,
            features="basic features"
        )
        # ✅ Assign tier when creating tenant
        self.tenant = Tenant.objects.create(
            name="TestTenant",
            email="tenant@example.com",
            tier=self.tier,
            status="active"
        )
        self.rbac = RBACMiddleware(lambda req: req)

    def make_tenant_user(self, email, role):
        user = User.objects.create_user(email=email, password="testpass123")
        TenantUser.objects.create(user=user, tenant=self.tenant, role=role)
        return user

    def test_owner_permissions(self):
        user = self.make_tenant_user("owner@example.com", "owner")
        request = self.factory.get("/")
        request.user = user
        request.tenant = self.tenant   # ✅ attach tenant
        self.rbac(request)
        self.assertIn("tenants:update", request.user.permissions)

    def test_admin_permissions(self):
        user = self.make_tenant_user("admin@example.com", "admin")
        request = self.factory.get("/")
        request.user = user
        request.tenant = self.tenant   # ✅ attach tenant
        self.rbac(request)
        self.assertIn("users:manage", request.user.permissions)

    def test_manager_permissions(self):
        user = self.make_tenant_user("manager@example.com", "manager")
        request = self.factory.get("/")
        request.user = user
        request.tenant = self.tenant   # ✅ attach tenant
        self.rbac(request)
        self.assertIn("customers:view", request.user.permissions)

    def test_user_permissions(self):
        user = self.make_tenant_user("user@example.com", "user")
        request = self.factory.get("/")
        request.user = user
        request.tenant = self.tenant   # ✅ attach tenant
        self.rbac(request)
        self.assertIn("invoices:view", request.user.permissions)

    def test_viewer_permissions(self):
        user = self.make_tenant_user("viewer@example.com", "viewer")
        request = self.factory.get("/")
        request.user = user
        request.tenant = self.tenant   # ✅ attach tenant
        self.rbac(request)
        self.assertIn("projects:view", request.user.permissions)
