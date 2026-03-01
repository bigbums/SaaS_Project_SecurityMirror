import factory
from django.contrib.auth import get_user_model
from saas_app.core.models import Tier, Tenant, TenantUser

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        # ✅ prevents the deprecation warning about postgeneration save
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "pass123")


class TierFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tier

    # ✅ generate unique names automatically
    name = factory.Sequence(lambda n: f"Tier {n}")
    features = factory.List([])
    max_users = 5
    max_locations = None
    price = 0


class TenantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tenant

    name = factory.Sequence(lambda n: f"Tenant {n}")
    email = factory.Sequence(lambda n: f"tenant{n}@example.com")
    tier = factory.SubFactory(TierFactory)


class TenantUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TenantUser

    tenant = factory.SubFactory(TenantFactory)
    user = factory.SubFactory(UserFactory)
    role = "owner"
