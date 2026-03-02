import django
import os
from datetime import datetime, timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saas_app.settings")
django.setup()

from core.models import CustomUser, SMEProfile, Tenant, TenantUser

# -----------------------------
# Create sample users with names
# -----------------------------
users_data = [
    {
        "email": "bigbums@gmail.com",
        "first_name": "Bunmi",
        "last_name": "Olawale",
        "password": "admin123",
        "date_joined": datetime.now() - timedelta(days=180),  # joined 6 months ago
        "last_login": datetime.now() - timedelta(days=1),     # logged in yesterday
    },
    {
        "email": "user1@example.com",
        "first_name": "Ada",
        "last_name": "Okafor",
        "password": "test123",
        "date_joined": datetime.now() - timedelta(days=90),   # joined 3 months ago
        "last_login": datetime.now() - timedelta(days=7),     # logged in last week
    },
    {
        "email": "user2@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "test123",
        "date_joined": datetime.now() - timedelta(days=30),   # joined 1 month ago
        "last_login": datetime.now() - timedelta(days=30),    # logged in last month
    },
]

created_users = []
for data in users_data:
    user, created = CustomUser.objects.get_or_create(
        email=data["email"],
        defaults={
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "password": data["password"],
            "is_active": True,
        },
    )
    # Update names and lifecycle fields if user already exists
    user.first_name = data["first_name"]
    user.last_name = data["last_name"]
    user.date_joined = data["date_joined"]
    user.last_login = data["last_login"]
    user.save()
    created_users.append(user)

superuser = created_users[0]
user1 = created_users[1]
user2 = created_users[2]

# -----------------------------
# Create SME Profiles
# -----------------------------
SMEProfile.objects.get_or_create(
    user=superuser,
    defaults={"company_name": "BigBums Ltd", "subscription_plan": "premium"}
)

SMEProfile.objects.get_or_create(
    user=user1,
    defaults={"company_name": "TechNova", "subscription_plan": "standard"}
)

# -----------------------------
# Create Tenants
# -----------------------------
tenant1, _ = Tenant.objects.get_or_create(
    name="Tenant Alpha",
    defaults={"email": "alpha@example.com", "tier": "premium", "status": "active", "storage_type": "cloud"}
)

tenant2, _ = Tenant.objects.get_or_create(
    name="Tenant Beta",
    defaults={"email": "beta@example.com", "tier": "standard", "status": "active", "storage_type": "local"}
)

# -----------------------------
# Link TenantUsers
# -----------------------------
TenantUser.objects.get_or_create(tenant=tenant1, user=superuser, defaults={"role": "Owner"})
TenantUser.objects.get_or_create(tenant=tenant1, user=user1, defaults={"role": "Manager"})
TenantUser.objects.get_or_create(tenant=tenant2, user=user2, defaults={"role": "Staff"})

print("✅ Seeding complete! Check Django Admin for Tenants, SMEProfiles, and TenantUsers with simulated date joined and last login.")
