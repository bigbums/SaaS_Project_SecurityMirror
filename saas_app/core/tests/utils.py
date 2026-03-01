from django.contrib.auth import get_user_model
from saas_app.core.models import Tier, Tenant

User = get_user_model()

def create_test_user_with_tenant(email="test@example.com", tier_name="Standard"):
    """
    Create a test user and fetch the Tenant created by the signal.
    Ensures the requested Tier exists and updates the tenant accordingly.
    """
    user = User.objects.create_user(email=email, password="pass123")

    # Ensure the tier exists
    tier, _ = Tier.objects.get_or_create(
        name=tier_name,
        defaults={"max_users": 10, "max_locations": 2, "price": 0, "hosting_type": "cloud"},
    )

    # Fetch the tenant created automatically by the signal
    tenant = Tenant.objects.get(email=email)

    # Update tenant tier if needed
    tenant.tier = tier
    tenant.save()

    return user, tenant
