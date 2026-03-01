import datetime
from django.core.management.base import BaseCommand
from django.apps import apps
from django.utils import timezone

class Command(BaseCommand):
    help = "Seed demo tenant, customers, and invoices"

    def add_arguments(self, parser):
        parser.add_argument("--tenant-name", type=str, default="Demo Tenant", help="Name of the tenant to seed")
        parser.add_argument("--amount", type=int, default=1000, help="Invoice amount")
        parser.add_argument("--currency", type=str, default="USD", help="Invoice currency (e.g. USD, NGN)")
        parser.add_argument("--status", type=str, default="pending", help="Invoice status (pending, paid, overdue)")
        parser.add_argument("--no-tenant-invoice", action="store_true", help="Skip seeding tenant invoice")
        parser.add_argument("--only-tenant-invoice", action="store_true", help="Seed only tenant invoice (skip platform invoice)")

    def handle(self, *args, **options):
        # Graceful conflict check
        if options.get("no_tenant_invoice") and options.get("only_tenant_invoice"):
            self.stdout.write(self.style.ERROR(
                "You cannot use --no-tenant-invoice and --only-tenant-invoice together."
            ))
            return

        tenant_name = options["tenant_name"]
        amount = options["amount"]
        currency = options["currency"]
        status = options["status"]

        Tier = apps.get_model("core", "Tier")
        Tenant = apps.get_model("core", "Tenant")
        PlatformCustomer = apps.get_model("core", "PlatformCustomer")
        PlatformInvoice = apps.get_model("core", "PlatformInvoice")
        TenantCustomer = apps.get_model("core", "TenantCustomer")
        TenantInvoice = apps.get_model("core", "TenantInvoice")

        # Ensure Free tier exists
        free_tier, created = Tier.objects.update_or_create(
            name="Free",
            defaults={"max_users": 3, "max_locations": 1, "price": 0},
        )
        self.stdout.write(self.style.SUCCESS(
            f"{'Created' if created else 'Updated'} tier '{free_tier.name}'"
        ))

        # Seed tenant
        demo_tenant, created = Tenant.objects.update_or_create(
            name=tenant_name,
            defaults={"email": "demo@example.com", "status": "active", "tier": free_tier},
        )
        self.stdout.write(self.style.SUCCESS(
            f"{'Created' if created else 'Updated'} tenant '{demo_tenant.name}'"
        ))

        # Seed platform customer
        demo_customer, created = PlatformCustomer.objects.update_or_create(
            email="default@example.com",
            defaults={"name": "Default Customer"},
        )
        self.stdout.write(self.style.SUCCESS(
            f"{'Created' if created else 'Updated'} platform customer '{demo_customer.name}'"
        ))

        # Seed platform invoice unless --only-tenant-invoice is set
        due_date = timezone.now().date() + datetime.timedelta(days=30)
        if not options.get("only_tenant_invoice"):
            platform_invoice, created = PlatformInvoice.objects.update_or_create(
                tenant=demo_tenant,
                customer=demo_customer,
                defaults={
                    "amount": amount,
                    "currency": currency,
                    "status": status,
                    "due_date": due_date,
                    "description": "Platform invoice generated",
                    "issued_at": timezone.now(),
                },
            )
            self.stdout.write(self.style.SUCCESS(
                f"{'Created' if created else 'Updated'} platform invoice for tenant '{demo_tenant.name}'"
            ))

        # Seed tenant customer
        tenant_customer, created = TenantCustomer.objects.update_or_create(
            tenant=demo_tenant,
            email="tenantcustomer@example.com",
            defaults={"name": "Tenant Customer"},
        )
        self.stdout.write(self.style.SUCCESS(
            f"{'Created' if created else 'Updated'} tenant customer '{tenant_customer.name}'"
        ))

        # Seed tenant invoice unless --no-tenant-invoice is set
        if not options.get("no_tenant_invoice"):
            tenant_invoice, created = TenantInvoice.objects.update_or_create(
                tenant=demo_tenant,
                customer=tenant_customer,
                defaults={
                    "amount": amount // 2,
                    "currency": currency,
                    "status": status,
                    "due_date": due_date,
                    "description": "Tenant invoice generated",
                    "issued_at": timezone.now(),
                },
            )
            self.stdout.write(self.style.SUCCESS(
                f"{'Created' if created else 'Updated'} tenant invoice for tenant '{demo_tenant.name}'"
            ))

        self.stdout.write(self.style.SUCCESS(
            f"Demo data seeded successfully for tenant '{tenant_name}' "
            f"with invoice amount {amount} {currency} and status '{status}'"
        ))
