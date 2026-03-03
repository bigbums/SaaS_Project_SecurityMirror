from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch import receiver
from saas_app.core.models import Tenant, TenantUser, PlatformTenantConfig, Tier, TenantInvoice, PlatformInvoice

@receiver(post_save, sender=Tenant)
def initialize_tenant_limits_and_config(sender, instance, created, raw, **kwargs):
    if created and not raw:
        instance.current_users_count = 0
        instance.current_locations_count = 0
        if not instance.tier:
            free_tier, _ = Tier.objects.get_or_create(
                name="Free",
                defaults={"max_users": 5, "max_locations": 1, "price": 0, "features": []},
            )
            instance.tier = free_tier
        instance.save()
        PlatformTenantConfig.objects.get_or_create(
            tenant=instance,
            defaults={"storage_type": "cloud", "hosting_type": "cloud"},
        )

@receiver(pre_delete, sender=Tenant)
def cleanup_tenant_invoices_before_delete(sender, instance, **kwargs):
    for invoice in TenantInvoice.objects.filter(tenant=instance):
        if invoice.pdf_file:
            invoice.pdf_file.delete(save=False)
        invoice.delete()
    for invoice in PlatformInvoice.objects.filter(tenant=instance):
        if invoice.pdf_file:
            invoice.pdf_file.delete(save=False)
        invoice.delete()

@receiver(post_delete, sender=Tenant)
def cleanup_tenant_related_data(sender, instance, **kwargs):
    TenantUser.objects.filter(tenant=instance).delete()
    PlatformTenantConfig.objects.filter(tenant=instance).delete()
