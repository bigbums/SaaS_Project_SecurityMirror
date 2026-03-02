from django.db import migrations
import datetime



import datetime

def seed_master_data(apps, schema_editor):
    Tier = apps.get_model("core", "Tier")
    Tenant = apps.get_model("core", "Tenant")
    PlatformCustomer = apps.get_model("core", "PlatformCustomer")
    PlatformInvoice = apps.get_model("core", "PlatformInvoice")
    TenantCustomer = apps.get_model("core", "TenantCustomer")
    TenantInvoice = apps.get_model("core", "TenantInvoice")

    # Seed tiers
    tiers = [
        {"name": "Free", "max_users": 3, "max_locations": 1, "price": 0},
        {"name": "Standard", "max_users": 10, "max_locations": 2, "price": 0},
        {"name": "Premium", "max_users": 50, "max_locations": 10, "price": 5000},
        {"name": "Enterprise", "max_users": 200, "max_locations": 50, "price": 20000},
    ]
    for t in tiers:
        Tier.objects.update_or_create(name=t["name"], defaults=t)

    # Seed tenant
    free_tier = Tier.objects.get(name="Free")
    demo_tenant, _ = Tenant.objects.update_or_create(
        name="Demo Tenant",
        defaults={"email": "demo@example.com", "status": "active", "tier": free_tier},
    )

    # Seed platform customer
    demo_customer, _ = PlatformCustomer.objects.update_or_create(
        email="default@example.com",
        defaults={"name": "Default Customer"},
    )

    # Seed platform invoice
    due_date = datetime.date.today() + datetime.timedelta(days=30)
    PlatformInvoice.objects.update_or_create(
        tenant=demo_tenant,
        customer=demo_customer,
        defaults={
            "amount": 1000,
            "currency": "USD",
            "status": "pending",
            "due_date": due_date,
            "description": "Platform invoice generated",
            "issued_at": datetime.datetime.now(),
        },
    )

    # Seed tenant customer
    tenant_customer, _ = TenantCustomer.objects.update_or_create(
        tenant=demo_tenant,
        email="tenantcustomer@example.com",
        defaults={"name": "Tenant Customer"},
    )

    # Seed tenant invoice
    TenantInvoice.objects.update_or_create(
        tenant=demo_tenant,
        customer=tenant_customer,
        defaults={
            "amount": 500,
            "currency": "NGN",
            "status": "pending",
            "due_date": due_date,
            "description": "Tenant invoice generated",
            "issued_at": datetime.datetime.now(),
        },
    )

class Migration(migrations.Migration):

    dependencies = [
        ("core", "0021_alter_platformcustomer_email_unique"),
    ]

    operations = [
        migrations.RunPython(seed_master_data),
    ]


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0021_alter_platformcustomer_email_unique"),
    ]

    operations = [
        migrations.RunPython(seed_master_data),
    ]
