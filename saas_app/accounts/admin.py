from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile
from saas_app.core.models import TenantUser, Tenant, Tier

class TenantFilter(admin.SimpleListFilter):
    title = "Tenant"
    parameter_name = "tenant"

    def lookups(self, request, model_admin):
        return [(t.id, t.name) for t in Tenant.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(tenantuser__tenant__id=self.value())
        return queryset

class TierFilter(admin.SimpleListFilter):
    title = "Tier"
    parameter_name = "tier"

    def lookups(self, request, model_admin):
        return [(tier.id, tier.name) for tier in Tier.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(tenantuser__tenant__tier__id=self.value())
        return queryset

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    inlines = [ProfileInline]
    list_display = ("email", "first_name", "last_name", "tenant_name", "tenant_tier", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active", "is_superuser", TenantFilter, TierFilter)
    ordering = ("email",)
    search_fields = ("email", "first_name", "last_name")

    def tenant_name(self, obj):
        tenant_user = TenantUser.objects.filter(user=obj).first()
        return tenant_user.tenant.name if tenant_user else "-"
    tenant_name.short_description = "Tenant"

    def tenant_tier(self, obj):
        tenant_user = TenantUser.objects.filter(user=obj).first()
        return tenant_user.tenant.tier.name if tenant_user and tenant_user.tenant.tier else "-"
    tenant_tier.short_description = "Tier"
