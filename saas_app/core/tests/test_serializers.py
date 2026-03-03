import pytest

from saas_app.core.models import Tenant, Tier, TenantUser
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from saas_app.core.serializers import TenantUserSerializer


User = get_user_model()

@pytest.mark.django_db
def test_tenant_user_serializer_can_create():
    user = User.objects.create_user(email="writer@example.com", password="pass")
    tier = Tier.objects.get(name="Standard")
    tenant = Tenant.objects.create(name="Tenant A", tier=tier)

    # Make user an owner so serializer passes validation
    TenantUser.objects.create(tenant=tenant, user=user, role="owner")

    tenant_user_data = {"user_id": user.id, "tenant_id": tenant.id, "role": "member"}

    factory = APIRequestFactory()
    request = factory.post("/fake-url/")
    request.user = user

    serializer = TenantUserSerializer(data=tenant_user_data, context={"request": request})
    assert serializer.is_valid(), serializer.errors
