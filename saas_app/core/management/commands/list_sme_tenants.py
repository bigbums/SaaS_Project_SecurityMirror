from django.core.management.base import BaseCommand
from saas_app.core.models import SmeProfile

class Command(BaseCommand):
    help = "List all tenants under an SME"

    def add_arguments(self, parser):
        parser.add_argument('--sme', type=str, help='SME name')

    def handle(self, *args, **options):
        sme_name = options['sme']
        try:
            sme = SmeProfile.objects.get(name=sme_name)
            for tenant in sme.tenants.all():
                self.stdout.write(f"{tenant.tenant_name} ({tenant.status})")
        except SmeProfile.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"SME '{sme_name}' not found"))
