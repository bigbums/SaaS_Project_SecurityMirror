from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from saas_app.core.middleware.TenantMiddleware import TenantMiddleware
from saas_app.core.models import Tenant, TenantUser, Tier

User = get_user_model()

class TenantMiddlewareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = TenantMiddleware(lambda req: req)

        # Create a Tier first
        self.tier = Tier.objects.create(name="Basic", max_users=10, max_locations=1, price=0)

        # Create a Tenant with a valid tier
        self.tenant = Tenant.objects.create(name="TestTenant", tier=self.tier, status="active")

    def make_user_with_tenant(self, email):
        user = User.objects.create_user(email=email, password="testpass123")
        TenantUser.objects.create(user=user, tenant=self.tenant)
        return user

    def test_authenticated_user_with_tenant(self):
        user = self.make_user_with_tenant("user_with_tenant@example.com")
        request = self.factory.get("/dummy-url")
        request.user = user
        self.middleware(request)
        self.assertIsNotNone(request.tenant)
        self.assertEqual(request.tenant.name, "TestTenant")

    def test_authenticated_user_without_tenant(self):
        user = User.objects.create_user(email="user_without_tenant@example.com", password="testpass123")
        request = self.factory.get("/dummy-url")
        request.user = user
        self.middleware(request)

    # Expect a default tenant (Free tier) to exist
        self.assertIsNotNone(request.tenant)
        self.assertEqual(request.tenant.tier.name, "Free")


    def test_anonymous_user(self):
        request = self.factory.get("/dummy-url")
        request.user = AnonymousUser()  # proper anonymous user
        self.middleware(request)
        self.assertIsNone(request.tenant)
