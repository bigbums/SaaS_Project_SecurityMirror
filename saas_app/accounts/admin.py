from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile
from saas_app.core.models import TenantUser

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    inlines = [ProfileInline]
    list_display = ("email", "first_name", "last_name", "tenant_name", "tenant_tier", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active", "is_superuser")
    ordering = ("email",)
    search_fields = ("email", "first_name", "last_name")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "password1", "password2", "is_staff", "is_active"),
        }),
    )

    def tenant_name(self, obj):
        tenant_user = TenantUser.objects.filter(user=obj).first()
        return tenant_user.tenant.name if tenant_user else "-"
    tenant_name.short_description = "Tenant"

    def tenant_tier(self, obj):
        tenant_user = TenantUser.objects.filter(user=obj).first()
        return tenant_user.tenant.tier.name if tenant_user and tenant_user.tenant.tier else "-"
    tenant_tier.short_description = "Tier"
