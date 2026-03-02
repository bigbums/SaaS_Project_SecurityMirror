from django.db import migrations

def seed_tiers(apps, schema_editor):
    Tier = apps.get_model("core", "Tier")

    tiers = [
        ("Free", [], 0, 5, 1),
        ("Standard", ["branding"], 50, 20, 5),
        ("Premium", ["branding", "invoice_customization"], 100, 50, 10),
        ("Enterprise", ["branding", "invoice_customization"], 500, 200, 50),
    ]

    for name, features, price, max_users, max_locations in tiers:
        Tier.objects.update_or_create(
            name=name,
            defaults={
                "features": features,
                "price": price,
                "max_users": max_users,
                "max_locations": max_locations,
            },
        )

def unseed_tiers(apps, schema_editor):
    Tier = apps.get_model("core", "Tier")
    Tier.objects.filter(name__in=["Free", "Standard", "Premium", "Enterprise"]).delete()

class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_remove_tier_hosting_type_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_tiers, reverse_code=unseed_tiers),
    ]
