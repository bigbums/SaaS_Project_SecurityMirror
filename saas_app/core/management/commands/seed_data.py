import csv
import json
import datetime
import os
import platform
from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage
from saas_app.core.models import SmeProfile, Tenant, TenantUser
from django.contrib.auth.models import User
from faker import Faker
import random

class Command(BaseCommand):
    help = "Seed the database with SMEs, Tenants, TenantUsers (safe checks, bunmi123, superadmin, default admins, summary with role breakdown, and CSV/JSON/email export options)"

    def add_arguments(self, parser):
        parser.add_argument('--smes', type=int, default=5, help='Number of SMEs to create')
        parser.add_argument('--tenants', type=int, default=10, help='Number of tenants to create')
        parser.add_argument('--users', type=int, default=20, help='Number of random users to create')
        parser.add_argument('--csv', type=str, help='Optional base filename for tenant summary CSV export')
        parser.add_argument('--json', type=str, help='Optional base filename for tenant summary JSON export')
        parser.add_argument('--no-open', action='store_true', help='Do not auto-open the CSV after export')
        parser.add_argument('--outdir', type=str, help='Directory to save the export files (default: current project root)')
        parser.add_argument('--email', type=str, help='Email address to send the exported file(s) to')

    def handle(self, *args, **kwargs):
        fake = Faker()

        num_smes = kwargs['smes']
        num_tenants = kwargs['tenants']
        num_users = kwargs['users']
        csv_base = kwargs.get('csv')
        json_base = kwargs.get('json')
        no_open = kwargs.get('no_open')
        outdir = kwargs.get('outdir') or os.getcwd()
        email_recipient = kwargs.get('email')

        tenants = []
        tenant_admin_map = {}

        # ... (seeding logic unchanged: SMEs, Tenants, Users, bunmi123, superadmin)

        # ✅ Print summary with role breakdown
        self.stdout.write(self.style.SUCCESS(
            f"\n✅ Seeded {num_smes} SMEs, {num_tenants} Tenants (each with a default admin), "
            f"{num_users} random users, plus bunmi123 and superadmin test users!\n"
        ))

        self.stdout.write("📋 Tenant Summary:\n")
        summary_rows = []
        for tenant in Tenant.objects.all():
            default_admin = tenant.users.filter(role="admin").first()
            default_admin_username = default_admin.user.username if default_admin else "N/A"
            total_users = tenant.users.count()
            admin_count = tenant.users.filter(role="admin").count()
            member_count = tenant.users.filter(role="member").count()
            self.stdout.write(
                f" - {tenant.tenant_name}: Default Admin = {default_admin_username}, "
                f"Total Users = {total_users} (Admins = {admin_count}, Members = {member_count})"
            )
            summary_rows.append({
                "tenant_name": tenant.tenant_name,
                "default_admin": default_admin_username,
                "total_users": total_users,
                "admins": admin_count,
                "members": member_count,
                "exported_at": datetime.datetime.now().isoformat()
            })

        exported_files = []

        # ✅ Export to CSV if requested
        if csv_base:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"{csv_base}_{timestamp}.csv"
            csv_path = os.path.join(outdir, csv_filename)
            os.makedirs(outdir, exist_ok=True)

            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Tenant Name", "Default Admin", "Total Users", "Admins", "Members", "Exported At"])
                for row in summary_rows:
                    writer.writerow([
                        row["tenant_name"], row["default_admin"], row["total_users"],
                        row["admins"], row["members"], row["exported_at"]
                    ])
            self.stdout.write(self.style.SUCCESS(f"\n📂 Tenant summary exported to {csv_path}"))
            exported_files.append(csv_path)

            if not no_open and platform.system() == "Windows":
                try:
                    os.startfile(csv_path)
                    self.stdout.write(self.style.SUCCESS("📖 CSV file opened in Excel"))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"⚠️ Could not auto-open CSV: {e}"))

        # ✅ Export to JSON if requested
        if json_base:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            json_filename = f"{json_base}_{timestamp}.json"
            json_path = os.path.join(outdir, json_filename)
            os.makedirs(outdir, exist_ok=True)

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(summary_rows, f, indent=4)
            self.stdout.write(self.style.SUCCESS(f"\n📂 Tenant summary exported to {json_path}"))
            exported_files.append(json_path)

        # ✅ Email the exported files if requested
        if email_recipient and exported_files:
            try:
                email = EmailMessage(
                    subject="Tenant Summary Report",
                    body="Attached are the tenant summary files generated by seed_data.",
                    to=[email_recipient]
                )
                for file_path in exported_files:
                    email.attach_file(file_path)
                email.send()
                self.stdout.write(self.style.SUCCESS(f"📧 Tenant summary emailed to {email_recipient}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"⚠️ Failed to send email: {e}"))
