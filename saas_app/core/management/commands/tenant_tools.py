from django.core.management.base import BaseCommand
from saas_app.core.models import SmeProfile, Tenant, TenantUser
from django.contrib.auth.models import User
from faker import Faker
import random

class Command(BaseCommand):
    help = "Seed the database with sample SMEs, Tenants, and TenantUsers (including bunmi123 and superadmin test users, plus default admins per tenant)"

    def add_arguments(self, parser):
        parser.add_argument('--smes', type=int, default=5, help='Number of SMEs to create')
        parser.add_argument('--tenants', type=int, default=10, help='Number of tenants to create')
        parser.add_argument('--users', type=int, default=20, help='Number of random users to create')

    def handle(self, *args, **kwargs):
        fake = Faker()

        num_smes = kwargs['smes']
        num_tenants = kwargs['tenants']
        num_users = kwargs['users']

        # Create SMEs
        smes = []
        for _ in range(num_smes):
            sme, _ = SmeProfile.objects.get_or_create(
                email=fake.unique.email(),
                defaults={
                    "name": fake.company()[:150],
                    "phone": fake.phone_number()[:50]
                }
            )
            smes.append(sme)

        # Controlled choices
        tiers = ['freemium', 'standard', 'premium', 'enterprise_premium']
        storage_types = ['shared', 'dedicated_schema', 'dedicated_db']
        statuses = ['active', 'suspended', 'terminated']
        roles = ['admin', 'member']

        # Create Tenants
        tenants = []
        for _ in range(num_tenants):
            sme = random.choice(smes)
            tenant, _ = Tenant.objects.get_or_create(
                sme=sme,
                tenant_name=(fake.company_suffix() + " Tenant")[:150],
                defaults={
                    "tier": random.choice(tiers),
                    "storage_type": random.choice(storage_types),
                    "db_schema": (fake.word() + "_schema")[:50],
                    "db_connection_string": fake.url()[:100],
                    "status": random.choice(statuses)
                }
            )
            tenants.append(tenant)

            # Ensure each tenant has a default admin
            default_admin_username = f"{tenant.tenant_name.lower().replace(' ', '_')}_admin"
            user, _ = User.objects.get_or_create(
                username=default_admin_username[:30],
                defaults={
                    "email": f"{default_admin_username}@example.com",
                    "first_name": "Default",
                    "last_name": "Admin"
                }
            )
            TenantUser.objects.get_or_create(
                tenant=tenant,
                user=user,
                defaults={"role": "admin"}
            )

        # Create random Users and link them to Tenants
        for _ in range(num_users):
            tenant = random.choice(tenants)
            username = fake.unique.user_name()[:30]
            email = fake.unique.email()
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "first_name": fake.first_name()[:30],
                    "last_name": fake.last_name()[:30]
                }
            )
            TenantUser.objects.get_or_create(
                tenant=tenant,
                user=user,
                defaults={"role": random.choice(roles)}
            )

        # Always create bunmi123 test user
        test_user, _ = User.objects.get_or_create(
            username="bunmi123",
            defaults={
                "email": "bunmi123@example.com",
                "first_name": "Bunmi",
                "last_name": "Test"
            }
        )
        if tenants:
            TenantUser.objects.get_or_create(
                tenant=tenants[0],
                user=test_user,
                defaults={"role": "admin"}
            )

        # Always create superadmin test user
        superadmin, _ = User.objects.get_or_create(
            username="superadmin",
            defaults={
                "email": "superadmin@example.com",
                "first_name": "Super",
                "last_name": "Admin"
            }
        )
        if tenants:
            TenantUser.objects.get_or_create(
                tenant=tenants[0],
                user=superadmin,
                defaults={"role": "admin"}
            )

        self.stdout.write(self.style.SUCCESS(
            f"✅ Seeded {num_smes} SMEs, {num_tenants} Tenants (each with a default admin), {num_users} random users, plus bunmi123 and superadmin test users!"
        ))
