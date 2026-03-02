from django.core.management.base import BaseCommand
from django.conf import settings
from saas_app.core.models import PlatformInvoice

class Command(BaseCommand):
    help = "Backfill platform_name field for all PlatformInvoice records"

    def handle(self, *args, **options):
        updated_count = 0
        for invoice in PlatformInvoice.objects.all():
            if not invoice.platform_name or invoice.platform_name.strip() == "":
                invoice.platform_name = settings.PLATFORM_COMPANY_NAME
                invoice.save(update_fields=["platform_name"])
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Backfill complete. Updated {updated_count} platform invoices."
        ))
