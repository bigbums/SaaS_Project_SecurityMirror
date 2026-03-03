from django.db.models.signals import post_delete
from django.dispatch import receiver
from saas_app.core.models import PlatformInvoice

@receiver(post_delete, sender=PlatformInvoice)
def cleanup_platform_invoice_file(sender, instance, **kwargs):
    if instance.pdf_file:
        instance.pdf_file.delete(save=False)
