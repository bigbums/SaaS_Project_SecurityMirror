import pytest
from saas_app.core.tests.factories import UserFactory, TenantFactory
from saas_app.core.models import TenantUser, Tier

@pytest.mark.django_db
@pytest.mark.parametrize("role", ["admin", "supervisor", "team lead", "manager", "member"])
def test_roles_are_assigned(role):
    users = [UserFactory(email=f"user{i}@example.com") for i in range(5)]
    tier = Tier.objects.get(name="Standard")
    tenant = TenantFactory(email=users[0].email, tier=tier)
    TenantUser.objects.create(tenant=tenant, user=users[0], role=role)
    assert tenant.users.filter(user=users[0], role=role).exists()


@pytest.mark.django_db
def test_all_roles_linked_to_tenant():
    users = [UserFactory(email=f"user{i}@example.com") for i in range(5)]
    tier = Tier.objects.get(name="Standard")
    tenant = TenantFactory(email=users[0].email, tier=tier)
    for i, role in enumerate(["admin", "supervisor", "team lead", "manager", "member"]):
        TenantUser.objects.create(tenant=tenant, user=users[i], role=role)
    assert all(tenant.users.filter(user=users[i], role=role).exists()
               for i, role in enumerate(["admin", "supervisor", "team lead", "manager", "member"]))


@pytest.mark.django_db
def test_random_user_not_linked_to_tenant():
    users = [UserFactory(email=f"user{i}@example.com") for i in range(5)]
    tier = Tier.objects.get(name="Standard")
    tenant = TenantFactory(email=users[0].email, tier=tier)
    TenantUser.objects.create(tenant=tenant, user=users[0], role="admin")
    random_user = UserFactory(email="random@example.com")
    assert not tenant.users.filter(user=random_user).exists()


@pytest.mark.django_db
def test_tenant_has_standard_tier():
    tier = Tier.objects.get(name="Standard")
    tenant = TenantFactory(tier=tier)
    assert tenant.tier.name == "Standard"


@pytest.mark.django_db
def test_user_is_linked_to_tenant():
    user = UserFactory(email="linked@example.com")
    tier = Tier.objects.get(name="Standard")
    tenant = TenantFactory(email=user.email, tier=tier)
    TenantUser.objects.create(tenant=tenant, user=user, role="member")
    assert tenant.users.filter(user=user).exists()


@pytest.mark.django_db
def test_other_user_not_linked_to_tenant():
    user = UserFactory(email="linked@example.com")
    other_user = UserFactory(email="other@example.com")
    tier = Tier.objects.get(name="Standard")
    tenant = TenantFactory(email=user.email, tier=tier)
    TenantUser.objects.create(tenant=tenant, user=user, role="member")
    assert not tenant.users.filter(user=other_user).exists()
