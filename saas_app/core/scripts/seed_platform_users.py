import json
import os
from django.core.management.base import BaseCommand
from saas_app.accounts.models import CustomUser
from saas_app.core.models import PlatformUser, Tenant, Tier
from django.db.models.signals import post_save
from saas_app.core.signals import assign_default_tenant_and_tier

class Command(BaseCommand):
    help = "Seed platform users with predefined roles or from a JSON file"

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help='Delete existing seeded platform users before recreating')
        parser.add_argument('--tier', type=str, default="Standard", help='Specify the tier name (default: Standard)')
        parser.add_argument('--tenant', type=str, default="DemoPlatformTenant", help='Specify the tenant name (default: DemoPlatformTenant)')
        parser.add_argument('--users-file', type=str, help='Path to JSON file containing user definitions')

    def handle(self, *args, **options):
        post_save.disconnect(assign_default_tenant_and_tier, sender=CustomUser)

        tier_name = options['tier']
        tenant_name = options['tenant']

        if options['reset']:
            self.stdout.write(self.style.WARNING("Resetting platform users..."))
            PlatformUser.objects.all().delete()
            CustomUser.objects.filter(email__in=[
                "platform_owner@demo.com",
                "platform_admin@demo.com",
                "platform_manager@demo.com",
                "platform_user@demo.com"
            ]).delete()
            Tenant.objects.filter(name=tenant_name).delete()
            Tier.objects.filter(name=tier_name).delete()

        # Load users either from file or fallback to defaults
        if options['users_file'] and os.path.exists(options['users_file']):
            with open(options['users_file'], 'r') as f:
                users = json.load(f)
            self.stdout.write(self.style.SUCCESS(f"Loaded users from {options['users_file']}"))
        else:
            users = [
                {"email": "platform_owner@demo.com", "first_name": "Alice", "last_name": "Johnson", "password": "OwnerPass123!", "role": "platform_owner"},
                {"email": "platform_admin@demo.com", "first_name": "Bob", "last_name": "Smith", "password": "AdminPass123!", "role": "platform_admin"},
                {"email": "platform_manager@demo.com", "first_name": "Carol", "last_name": "Williams", "password": "ManagerPass123!", "role": "platform_manager"},
                {"email": "platform_user@demo.com", "first_name": "David", "last_name": "Brown", "password": "UserPass123!", "role": "platform_user"},
            ]

        # Ensure Tier and Tenant exist
        tier, _ = Tier.objects.update_or_create(
            name=tier_name,
            defaults={"price": 0, "max_users": 10, "max_locations": 5}
        )
        tenant, _ = Tenant.objects.update_or_create(
            name=tenant_name,
            defaults={"status": "active", "tier": tier}
        )

        for u in users:
            user, _ = CustomUser.objects.update_or_create(
                email=u["email"],
                defaults={
                    "first_name": u["first_name"],
                    "last_name": u["last_name"],
                    "is_active": True,
                    "is_staff": False,
                }
            )
            user.set_password(u["password"])
            user.save()
            self.stdout.write(self.style.SUCCESS(f"User {u['email']} ensured/updated"))

            platform_user, _ = PlatformUser.objects.update_or_create(
                user=user,
                defaults={"role": u["role"]}
            )
            self.stdout.write(self.style.SUCCESS(f"PlatformUser {u['email']} role ensured/updated"))

        post_save.connect(assign_default_tenant_and_tier, sender=CustomUser)

