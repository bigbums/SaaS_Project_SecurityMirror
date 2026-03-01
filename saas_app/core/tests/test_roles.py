import pytest
from saas_app.core.tests.factories import UserFactory, TenantFactory, TenantUserFactory
from saas_app.core.models import TenantUser, Tier

@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_index, role",
    [
        (0, "admin"),
        (1, "supervisor"),
        (2, "team lead"),
        (3, "manager"),
        (4, "member"),
    ],
)
def test_roles_assigned_to_correct_users(user_index, role):
    users = [UserFactory(email=f"user{i}@example.com") for i in range(5)]

    # ✅ Reuse seeded tier instead of creating duplicate
    tier = Tier.objects.get(name="Standard")

    # ✅ Pass the existing tier into TenantFactory
    tenant = TenantFactory(email=users[0].email, tier=tier)

    # Link the user with the tenant and assign the role
    TenantUser.objects.create(tenant=tenant, user=users[user_index], role=role)

    # Assertion: user with the given role is linked to the tenant
    assert tenant.users.filter(user=users[user_index], role=role).exists()
