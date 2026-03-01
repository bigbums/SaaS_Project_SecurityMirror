from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "Find which tenant a user belongs to"

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username')

    def handle(self, *args, **options):
        username = options['username']
        try:
            user = User.objects.get(username=username)
            tenant = user.tenantuser.tenant
            self.stdout.write(f"User {username} belongs to tenant {tenant.tenant_name}")
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"User '{username}' not found"))
