from django.db import migrations

def seed_tiers(apps, schema_editor):
    Tier = apps.get_model("core", "Tier")
    Tier.objects.get_or_create(
        name="Free",
        defaults={"max_users": 5, "max_locations": 1, "price": 0, "hosting_type": "cloud"},
    )
    Tier.objects.get_or_create(
        name="Standard",
        defaults={"max_users": 20, "max_locations": 5, "price": 50, "hosting_type": "cloud"},
    )
    Tier.objects.get_or_create(
        name="Premium",
        defaults={"max_users": 100, "max_locations": 20, "price": 200, "hosting_type": "cloud"},
    )

class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_platformtenantconfig"),
    ]

    operations = [
        migrations.RunPython(seed_tiers),
    ]
