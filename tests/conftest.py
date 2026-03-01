import pytest
from django.contrib.auth import get_user_model
from saas_app.core.models import Tenant, TenantInvoice, TenantCustomer, Tier
from datetime import date

User = get_user_model()

@pytest.fixture
def user_factory(db):
    def create_user(**kwargs):
        defaults = {
            "email": "test@example.com",
            "password": "password123",
        }
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)
    return create_user

@pytest.fixture
def tenant_factory(db):
    def create_tenant(**kwargs):
        tier = kwargs.pop("tier", Tier.objects.first() or Tier.objects.create(name="Free"))
        defaults = {"name": "Test Tenant", "email": "tenant@example.com", "tier": tier}
        defaults.update(kwargs)
        return Tenant.objects.create(**defaults)
    return create_tenant

@pytest.fixture
def invoice_factory(db, tenant_factory):
    def create_invoice(**kwargs):
        tenant = kwargs.pop("tenant", tenant_factory())
        # Always create a customer if not provided
        customer = kwargs.pop("customer", TenantCustomer.objects.create(
            tenant=tenant,
            name="Test Customer",
            email="cust@example.com"
        ))
        defaults = {
            "tenant": tenant,
            "customer": customer,
            "amount": 1000,
            "currency": "NGN",
            "due_date": date.today(),
            "status": "pending",
        }
        defaults.update(kwargs)
        return TenantInvoice.objects.create(**defaults)
    return create_invoice
