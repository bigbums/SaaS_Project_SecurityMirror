from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, SMEProfile, Tenant, TenantUser, Project


# -----------------------------
# Project Admin
# -----------------------------
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "status", "created_at")
    search_fields = ("name",)
    list_filter = ("status", "created_at")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"


# -----------------------------
# SMEProfile Admin
# -----------------------------
@admin.register(SMEProfile)
class SMEProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "subscription_plan", "phone", "email")
    readonly_fields = ("subscription_plan",)

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if obj and obj.subscription_plan == "free":
            fields += ["logo", "address", "phone", "email"]
        return fields


# -----------------------------
# CustomUser Admin
# -----------------------------
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = (
        "email",
        "first_name",
        "last_name",
        "sme_company",
        "tenant_list",
        "date_joined",
        "last_login",
        "is_staff",
        "is_active",
    )
    list_filter = ("is_staff", "is_active")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "is_staff", "is_active")}
        ),
    )
    search_fields = (
        "email",
        "first_name",
        "last_name",
        "sme_profiles__name",
        "tenant_users__tenant__name",
    )
    ordering = ("email",)

    def sme_company(self, obj):
        return obj.sme_profiles.first().name if obj.sme_profiles.exists() else "-"
    sme_company.short_description = "SME Profile"

    def tenant_list(self, obj):
        tenants = obj.tenant_users.all()
        return ", ".join([tu.tenant.name for tu in tenants]) if tenants else "-"
    tenant_list.short_description = "Tenants"


# -----------------------------
# TenantUser Inline (inside Tenant)
# -----------------------------
class TenantUserInline(admin.TabularInline):
    model = TenantUser
    extra = 1
    fields = ("user", "role")
    autocomplete_fields = ("user",)


# -----------------------------
# Tenant Admin
# -----------------------------
@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "tier", "status", "storage_type", "created_at"]
    search_fields = ["name", "email"]
    list_filter = ["tier", "status", "storage_type"]
    inlines = [TenantUserInline]


# -----------------------------
# TenantUser Admin (separate view)
# -----------------------------
@admin.register(TenantUser)
class TenantUserAdmin(admin.ModelAdmin):
    list_display = (
        "user_email",
        "user_first_name",
        "user_last_name",
        "tenant_name",
        "role",
        "user_date_joined",
        "user_last_login",
    )
    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
        "tenant__name",
        "role",
    )
    list_filter = ("role", "tenant__tier", "tenant__status")

    def user_email(self, obj):
        return obj.user.email
    def user_first_name(self, obj):
        return obj.user.first_name
    def user_last_name(self, obj):
        return obj.user.last_name
    def tenant_name(self, obj):
        return obj.tenant.name
    def user_date_joined(self, obj):
        return obj.user.date_joined
    def user_last_login(self, obj):
        return obj.user.last_login
