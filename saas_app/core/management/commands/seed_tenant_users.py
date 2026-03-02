import json
import os
import yaml   # pip install pyyaml
from django.core.management.base import BaseCommand
from saas_app.accounts.models import CustomUser
from saas_app.core.models import Tenant, TenantUser, Tier
from django.db.models.signals import post_save
from saas_app.core.signals import assign_default_tenant_and_tier

class Command(BaseCommand):
    help = "Seed tenant users with predefined roles or from a JSON/YAML file"

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help='Delete existing seeded tenant users/tenants/tiers before recreating')
        parser.add_argument('--tier', type=str, default="Standard", help='Specify the tier name (default: Standard)')
        parser.add_argument('--tenant', type=str, default="DemoTenant", help='Specify the tenant name (default: DemoTenant)')
        parser.add_argument('--users-file', type=str, help='Path to JSON or YAML file containing tenant user definitions')
        parser.add_argument('--format', type=str, choices=['json', 'yaml'], help='Explicitly specify file format (json or yaml). If omitted, inferred from extension.')

    def handle(self, *args, **options):
        post_save.disconnect(assign_default_tenant_and_tier, sender=CustomUser)

        tier_name = options['tier']
        tenant_name = options['tenant']

        if options['reset']:
            self.stdout.write(self.style.WARNING("Resetting tenant data..."))
            TenantUser.objects.all().delete()
            Tenant.objects.filter(name=tenant_name).delete()
            Tier.objects.filter(name=tier_name).delete()
            CustomUser.objects.filter(email__in=[
                "tenant_owner@demo.com",
                "tenant_manager@demo.com",
                "tenant_member@demo.com"
            ]).delete()

        users = None
        if options['users_file'] and os.path.exists(options['users_file']):
            with open(options['users_file'], 'r') as f:
                if options.get('format') == 'yaml' or options['users_file'].endswith(('.yaml', '.yml')):
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)

                if "tenant_users" in data:
                    users = data["tenant_users"]
                else:
                    users = data
            self.stdout.write(self.style.SUCCESS(f"Loaded tenant users from {options['users_file']}"))

        if not users:
            users = [
                {"email": "tenant_owner@demo.com", "first_name": "Eve", "last_name": "Taylor", "password": "OwnerPass123!", "role": "owner"},
                {"email": "tenant_manager@demo.com", "first_name": "Frank", "last_name": "Lee", "password": "ManagerPass123!", "role": "manager"},
                {"email": "tenant_member@demo.com", "first_name": "Grace", "last_name": "Kim", "password": "MemberPass123!", "role": "member"},
            ]

        tier, _ = Tier.objects.update_or_create(name=tier_name, defaults={"price": 0, "max_users": 10, "max_locations": 5})
        self.stdout.write(self.style.SUCCESS(f"Tier '{tier_name}' ensured/updated"))

        tenant, _ = Tenant.objects.update_or_create(name=tenant_name, defaults={"status": "active", "tier": tier})
        self.stdout.write(self.style.SUCCESS(f"Tenant '{tenant_name}' ensured/updated"))

        for u in users:
            user, _ = CustomUser.objects.update_or_create(
                email=u["email"],
                defaults={"first_name": u["first_name"], "last_name": u["last_name"], "is_active": True, "is_staff": False}
            )
            user.set_password(u["password"])
            user.save()
            self.stdout.write(self.style.SUCCESS(f"User {u['email']} ensured/updated"))

            tenant_user, _ = TenantUser.objects.update_or_create(user=user, tenant=tenant, defaults={"role": u["role"]})
            self.stdout.write(self.style.SUCCESS(f"TenantUser {u['email']} role ensured/updated"))

        post_save.connect(assign_default_tenant_and_tier, sender=CustomUser)
