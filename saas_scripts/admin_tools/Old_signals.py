from django.db.models.signals import pre_save, post_save, post_delete, pre_delete
from django.dispatch import receiver
import logging
from django.utils.timezone import now
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.contrib.auth import get_user_model

from saas_app.core.utils.logging_helpers import log_json
from saas_app.core.models import (
    Tier, Tenant, TenantUser, PlatformTenantConfig,
    TenantInvoice, PlatformInvoice
)

User = get_user_model()

# ----------------------------
# TenantInvoice signals
# ----------------------------

@receiver(pre_save, sender=TenantInvoice)
def set_tenant_name(sender, instance, **kwargs):
    """Ensure tenant_name is always populated before saving TenantInvoice."""
    if instance.tenant and not instance.tenant_name:
        instance.tenant_name = instance.tenant.name


@receiver(post_delete, sender=TenantInvoice)
def cleanup_tenant_invoice_file(sender, instance, **kwargs):
    """Remove PDF file when a TenantInvoice is deleted."""
    if instance.pdf_file:
        instance.pdf_file.delete(save=False)


# ----------------------------
# PlatformInvoice signals
# ----------------------------

@receiver(post_delete, sender=PlatformInvoice)
def cleanup_platform_invoice_file(sender, instance, **kwargs):
    """Remove PDF file when a PlatformInvoice is deleted."""
    if instance.pdf_file:
        instance.pdf_file.delete(save=False)


# ----------------------------
# User signals
# ----------------------------

@receiver(post_save, sender=User)
def assign_default_tenant_and_tier(sender, instance, created, raw, **kwargs):
    """Assign a default tenant and free tier when a new user is created."""
    if created and not raw:
        free_tier, _ = Tier.objects.get_or_create(
            name="Free",
            defaults={"max_users": 5, "max_locations": 1, "price": 0, "features": []},
        )
        tenant = Tenant.objects.create(
            name=f"{instance.email}'s Tenant",
            email=instance.email,
            tier=free_tier,
            status="active",
        )
        TenantUser.objects.create(tenant=tenant, user=instance, role="owner")


@receiver(post_delete, sender=User)
def cleanup_user_related_data(sender, instance, **kwargs):
    """Remove TenantUser records when a User is deleted."""
    TenantUser.objects.filter(user=instance).delete()


# ----------------------------
# Tenant signals
# ----------------------------

@receiver(post_save, sender=Tenant)
def initialize_tenant_limits_and_config(sender, instance, created, raw, **kwargs):
    """Initialize tenant limits and config when a new Tenant is created."""
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
    """Clean up invoices before a Tenant is deleted."""
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
    """Remove TenantUser and PlatformTenantConfig records when a Tenant is deleted."""
    TenantUser.objects.filter(tenant=instance).delete()
    PlatformTenantConfig.objects.filter(tenant=instance).delete()


# ----------------------------
# Security logging signals
# ----------------------------

security_logger = logging.getLogger("security")

def log_failed_login(sender, credentials, request, **kwargs):
    """Log failed login attempts with structured JSON."""
    log_entry = {
        "event": "failed_login",
        "message": "failed login attempt",
        "user": credentials.get("username"),
        "ip": request.META.get("REMOTE_ADDR"),
        "path": request.path,
    }
    log_json(security_logger, "warning", log_entry, request=request)

user_login_failed.connect(log_failed_login)


def update_login(sender, user, request, **kwargs):
    """Update last_login timestamps for tenant and platform users."""
    if hasattr(user, "tenantuser"):
        user.tenantuser.last_login = now()
        user.tenantuser.save()
    if hasattr(user, "platformuser"):
        user.platformuser.last_login = now()
        user.platformuser.save()


def update_logout(sender, user, request, **kwargs):
    """Update last_logout timestamps for tenant and platform users."""
    if hasattr(user, "tenantuser"):
        user.tenantuser.last_logout = now()
        user.tenantuser.save()
    if hasattr(user, "platformuser"):
        user.platformuser.last_logout = now()
        user.platformuser.save()

user_logged_in.connect(update_login)
user_logged_out.connect(update_logout)
