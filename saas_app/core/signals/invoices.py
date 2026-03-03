from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from saas_app.core.models import TenantInvoice

@receiver(pre_save, sender=TenantInvoice)
def set_tenant_name(sender, instance, **kwargs):
    if instance.tenant and not instance.tenant_name:
        instance.tenant_name = instance.tenant.name

@receiver(post_delete, sender=TenantInvoice)
def cleanup_tenant_invoice_file(sender, instance, **kwargs):
    if instance.pdf_file:
        instance.pdf_file.delete(save=False)
