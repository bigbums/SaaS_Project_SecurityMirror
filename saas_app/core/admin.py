from django.contrib import admin
from .models import Tier, Tenant, TenantUser, Project, Item, Sale, SaleItem, Location, PlatformTenantConfig
from saas_app.core.models import PlatformUser

# -----------------------------
# Platform Users (restricted)
# -----------------------------
@admin.register(PlatformUser)
class PlatformUserAdmin(admin.ModelAdmin):
    list_display = ("user", "role")
    list_filter = ("role",)

    def has_add_permission(self, request):
        # Only superusers or platform owners/admins can add
        if request.user.is_superuser:
            return True
        platform_user = getattr(request.user, "platformuser", None)
        if platform_user and platform_user.role in ["platform_owner", "platform_admin"]:
            return True
        return False

    def has_change_permission(self, request, obj=None):
        return self.has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.has_add_permission(request)


# -----------------------------
# Tenants
# -----------------------------
@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "email", "tier", "status"]
    list_filter = ["tier", "status"]


# -----------------------------
# Tenant Users
# -----------------------------
@admin.register(TenantUser)
class TenantUserAdmin(admin.ModelAdmin):
    list_display = ["id", "tenant", "user", "role"]
    list_filter = ["role", "tenant"]


# -----------------------------
# Tiers
# -----------------------------
@admin.register(Tier)
class TierAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "max_users", "max_locations", "features")
    list_filter = ("name",)


# -----------------------------
# Locations
# -----------------------------
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "created_at")
    list_filter = ("tenant",)


# -----------------------------
# Platform Tenant Config
# -----------------------------
@admin.register(PlatformTenantConfig)
class PlatformTenantConfigAdmin(admin.ModelAdmin):
    list_display = ("tenant", "hosting_type", "storage_type", "notes")
    list_filter = ("hosting_type", "storage_type")
