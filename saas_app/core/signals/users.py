from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from saas_app.core.models import Tenant, TenantUser, Tier

User = get_user_model()

@receiver(post_save, sender=User)
def assign_default_tenant_and_tier(sender, instance, created, raw, **kwargs):
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
    TenantUser.objects.filter(user=instance).delete()
