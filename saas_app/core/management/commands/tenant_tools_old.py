from django.core.management.base import BaseCommand
from core.models import SmeProfile, Tenant, TenantUser
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "Tenant tools: run queries and manage user roles with admin safeguard"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="action", help="Available actions")

        # Existing sub-options...
        parser_users = subparsers.add_parser("list_tenant_users", help="List all users for a tenant")
        parser_users.add_argument("--tenant", type=str, required=True, help="Tenant name")
        parser_users.add_argument("--role", type=str, choices=["admin", "member"], help="Filter by role")

        parser_find = subparsers.add_parser("find_user_tenant", help="Find tenant and role for a user")
        parser_find.add_argument("--username", type=str, required=True, help="Username")

        parser_sme = subparsers.add_parser("list_sme_tenants", help="List tenants under an SME")
        parser_sme.add_argument("--sme", type=str, required=True, help="SME name")

        parser_sme_users = subparsers.add_parser("list_sme_users", help="List all users across an SME")
        parser_sme_users.add_argument("--sme", type=str, required=True, help="SME name")
        parser_sme_users.add_argument("--role", type=str, choices=["admin", "member"], help="Filter by role")

        # NEW: Promote/Demote user role with safeguard
        parser_set_role = subparsers.add_parser("set_user_role", help="Change a user's role in their tenant")
        parser_set_role.add_argument("--username", type=str, required=True, help="Target username")
        parser_set_role.add_argument("--role", type=str, choices=["admin", "member"], required=True, help="New role")
        parser_set_role.add_argument("--by", type=str, required=True, help="Username of the acting admin")

    def handle(self, *args, **options):
        action = options["action"]

        if action == "set_user_role":
            target_username = options["username"]
            new_role = options["role"]
            acting_username = options["by"]

            try:
                # Acting user must exist and be an admin in the same tenant
                acting_user = User.objects.get(username=acting_username)
                acting_tu = acting_user.tenantuser
                if acting_tu.role != "admin":
                    self.stdout.write(self.style.ERROR(
                        f"❌ Permission denied: {acting_username} is not an admin."
                    ))
                    return

                # Target user must exist and belong to the same tenant
                target_user = User.objects.get(username=target_username)
                target_tu = target_user.tenantuser
                if target_tu.tenant != acting_tu.tenant:
                    self.stdout.write(self.style.ERROR(
                        f"❌ Permission denied: {target_username} belongs to a different tenant."
                    ))
                    return

                # Update role
                target_tu.role = new_role
                target_tu.save()
                self.stdout.write(self.style.SUCCESS(
                    f"✅ {acting_username} changed {target_username}'s role to '{new_role}' in tenant '{target_tu.tenant.tenant_name}'"
                ))

            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR("❌ One of the specified users does not exist"))
            except TenantUser.DoesNotExist:
                self.stdout.write(self.style.ERROR("❌ One of the specified users is not linked to any tenant"))
