from django.core.management.base import BaseCommand
from saas_app.core.models import TenantInvoice

class Command(BaseCommand):
    help = "Backfill tenant_name field for all TenantInvoice records"

    def handle(self, *args, **options):
        updated_count = 0
        for invoice in TenantInvoice.objects.all():
            if invoice.tenant and not invoice.tenant_name:
                invoice.tenant_name = invoice.tenant.name
                invoice.save(update_fields=["tenant_name"])
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Backfill complete. Updated {updated_count} invoices."
        ))
