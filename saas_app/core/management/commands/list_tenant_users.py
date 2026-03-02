from django.core.management.base import BaseCommand
from saas_app.core.models import TenantUser

class Command(BaseCommand):
    help = "List all users for a given tenant"

    def add_arguments(self, parser):
        parser.add_argument('--tenant', type=str, help='Tenant name')

    def handle(self, *args, **options):
        tenant_name = options['tenant']
        if not tenant_name:
            self.stdout.write(self.style.ERROR("Please provide --tenant"))
            return

        try:
            from saas_app.core.models import Tenant
            tenant = Tenant.objects.get(tenant_name=tenant_name)
            for tu in tenant.users.all():
                self.stdout.write(f"{tu.user.username} ({tu.role})")
        except Tenant.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Tenant '{tenant_name}' not found"))
