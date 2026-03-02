import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from saas_app.core.models import Tenant, TenantCustomer, TenantInvoice, PlatformInvoice

class Command(BaseCommand):
    help = "Seed demo tenant and platform invoices with randomized data (with cleanup)"

    def handle(self, *args, **options):
        tenant = Tenant.objects.first()
        if not tenant:
            self.stdout.write(self.style.ERROR("No Tenant found. Please create one first."))
            return

        # Ensure at least one customer exists
        customer, created = TenantCustomer.objects.get_or_create(
            tenant=tenant,
            email="demo.customer@example.com",
            defaults={"name": "Demo Customer"}
        )

        statuses = ["pending", "paid", "overdue"]

        # 🔥 Cleanup old demo invoices before seeding new ones
        TenantInvoice.objects.filter(customer=customer).delete()
        PlatformInvoice.objects.filter(tenant=tenant).delete()

        # Create sample tenant invoices
        for i in range(5):
            TenantInvoice.objects.create(
                tenant=tenant,
                customer=customer,
                amount=random.choice([100, 150, 200, 250, 300]),
                currency="USD",
                due_date=timezone.now().date() + timedelta(days=random.randint(0, 30)),
                status=random.choice(statuses)
            )

        # Create sample platform invoices
        for i in range(5):
            PlatformInvoice.objects.create(
                tenant=tenant,
                amount=random.choice([250, 350, 450, 550]),
                currency="USD",
                due_date=timezone.now().date() + timedelta(days=random.randint(0, 30)),
                status=random.choice(statuses)
            )

        self.stdout.write(self.style.SUCCESS("Cleaned old demo invoices and seeded new randomized ones."))
