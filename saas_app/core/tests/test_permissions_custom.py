import pytest
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from django.contrib.auth import get_user_model
from saas_app.core.models import Tenant, TenantUser, Tier, Item

User = get_user_model()


@pytest.mark.django_db
def test_owner_can_add_tenant_user():
    client = APIClient()
    owner = User.objects.create_user(email="owner@example.com", password="pass123")
    client.force_authenticate(user=owner)

    tier = Tier.objects.get(name="Standard")
    tenant = Tenant.objects.create(name="TestTenant", email="tenant@example.com", tier=tier)
    TenantUser.objects.create(tenant=tenant, user=owner, role="owner")

    new_user = User.objects.create_user(email="new@example.com", password="pass123")

    url = reverse("v1:tenantuser-list")   # 👈 namespaced
    response = client.post(url, {"tenant_id": tenant.id, "user_id": new_user.id, "role": "member"}, format="json")

    assert response.status_code == 201
    assert response.data["role"] == "member"
    assert response.data["user"]["email"] == "new@example.com"


@pytest.mark.django_db
def test_non_owner_cannot_add_tenant_user():
    client = APIClient()
    member = User.objects.create_user(email="member@example.com", password="pass123")
    client.force_authenticate(user=member)

    tier = Tier.objects.get(name="Standard")
    tenant = Tenant.objects.create(name="TestTenant", email="tenant@example.com", tier=tier)
    TenantUser.objects.create(tenant=tenant, user=member, role="member")

    new_user = User.objects.create_user(email="new@example.com", password="pass123")

    url = reverse("v1:tenantuser-list")   # 👈 namespaced
    response = client.post(url, {"tenant_id": tenant.id, "user_id": new_user.id, "role": "member"}, format="json")

    assert response.status_code == 403


@pytest.mark.django_db
def test_owner_can_update_tenant_user_role():
    client = APIClient()
    owner = User.objects.create_user(email="owner@example.com", password="pass123")
    client.force_authenticate(user=owner)

    tier = Tier.objects.get(name="Standard")
    tenant = Tenant.objects.create(name="TestTenant", email="tenant@example.com", tier=tier)
    TenantUser.objects.create(tenant=tenant, user=owner, role="owner")

    member_user = User.objects.create_user(email="member@example.com", password="pass123")
    tenant_user = TenantUser.objects.create(tenant=tenant, user=member_user, role="member")

    url = reverse("v1:tenantuser-detail", args=[tenant_user.id])   # 👈 namespaced
    response = client.patch(url, {"role": "manager"}, format="json")

    assert response.status_code == 200
    assert response.data["role"] == "manager"


@pytest.mark.django_db
def test_non_owner_cannot_update_tenant_user_role():
    client = APIClient()
    member = User.objects.create_user(email="member@example.com", password="pass123")
    client.force_authenticate(user=member)

    tier = Tier.objects.get(name="Standard")
    tenant = Tenant.objects.create(name="TestTenant", email="tenant@example.com", tier=tier)
    TenantUser.objects.create(tenant=tenant, user=member, role="member")

    other_user = User.objects.create_user(email="other@example.com", password="pass123")
    tenant_user = TenantUser.objects.create(tenant=tenant, user=other_user, role="member")

    url = reverse("v1:tenantuser-detail", args=[tenant_user.id])   # 👈 namespaced
    response = client.patch(url, {"role": "manager"}, format="json")

    assert response.status_code == 403


@pytest.mark.django_db
def test_owner_can_delete_tenant_user():
    client = APIClient()
    owner = User.objects.create_user(email="owner@example.com", password="pass123")
    client.force_authenticate(user=owner)

    tier = Tier.objects.get(name="Standard")
    tenant = Tenant.objects.create(name="TestTenant", email="tenant@example.com", tier=tier)
    TenantUser.objects.create(tenant=tenant, user=owner, role="owner")

    member_user = User.objects.create_user(email="member@example.com", password="pass123")
    tenant_user = TenantUser.objects.create(tenant=tenant, user=member_user, role="member")

    url = reverse("v1:tenantuser-detail", args=[tenant_user.id])   # 👈 namespaced
    response = client.delete(url)

    assert response.status_code == 204
    assert not TenantUser.objects.filter(id=tenant_user.id).exists()


@pytest.mark.django_db
def test_non_owner_cannot_delete_tenant_user():
    client = APIClient()
    member = User.objects.create_user(email="member@example.com", password="pass123")
    client.force_authenticate(user=member)

    tier = Tier.objects.get(name="Standard")
    tenant = Tenant.objects.create(name="TestTenant", email="tenant@example.com", tier=tier)
    TenantUser.objects.create(tenant=tenant, user=member, role="member")

    other_user = User.objects.create_user(email="other@example.com", password="pass123")
    tenant_user = TenantUser.objects.create(tenant=tenant, user=other_user, role="member")

    url = reverse("v1:tenantuser-detail", args=[tenant_user.id])   # 👈 namespaced
    response = client.delete(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_items_are_scoped_to_tenant():
    client = APIClient()
    owner1 = User.objects.create_user(email="owner1@example.com", password="pass123")
    owner2 = User.objects.create_user(email="owner2@example.com", password="pass123")

    tier = Tier.objects.get(name="Standard")
    tenant1 = Tenant.objects.create(name="Tenant1", email="t1@example.com", tier=tier)
    tenant2 = Tenant.objects.create(name="Tenant2", email="Tenant2@example.com", tier=tier)

    TenantUser.objects.create(tenant=tenant1, user=owner1, role="owner")
    TenantUser.objects.create(tenant=tenant2, user=owner2, role="owner")

    Item.objects.create(tenant=tenant1, name="Item1", type="product", price=10, stock=5)
    Item.objects.create(tenant=tenant2, name="Item2", type="service", price=20, stock=0)

    # Owner1 should only see Item1
    client.force_authenticate(user=owner1)
    url = reverse("v1:item-list")   # 👈 namespaced
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["name"] == "Item1"

    # Owner2 should only see Item2
    client.force_authenticate(user=owner2)
    response = client.get(url)
    assert len(response.data) == 1
    assert response.data[0]["name"] == "Item2"
