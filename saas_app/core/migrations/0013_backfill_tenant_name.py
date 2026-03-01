from django.db import migrations

def backfill_tenant_name(apps, schema_editor):
    TenantInvoice = apps.get_model("core", "TenantInvoice")
    for invoice in TenantInvoice.objects.all():
        if invoice.tenant and not invoice.tenant_name:
            invoice.tenant_name = invoice.tenant.name
            invoice.save(update_fields=["tenant_name"])

class Migration(migrations.Migration):

    dependencies = [
        ("core", "0012_platformpayment_proof_file_and_more"),  # latest migration
    ]

    operations = [
        migrations.RunPython(backfill_tenant_name),
    ]
