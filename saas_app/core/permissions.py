# saas_app/core/permissions.py
from rest_framework import permissions
from rest_framework.permissions import BasePermission
from saas_app.core.utils.features import has_feature
from saas_app.core.models import TenantUser, PlatformUser, Tenant
from saas_app.core.config.privileges import role_privileges

class RequireFeaturePermission(permissions.BasePermission):
    def __init__(self, feature_name):
        self.feature_name = feature_name

    def has_permission(self, request, view):
        tenant_user = getattr(request.user, "tenantuser_set", None)
        if tenant_user:
            tenant = tenant_user.first().tenant
            tier = tenant.tier
            return has_feature(tier, self.feature_name)
        return False

class RequireBrandingPermission(BasePermission):
    def has_permission(self, request, view):
        tenant = getattr(request, "tenant", None)
        if tenant:
            return "branding" in tenant.tier.features
        tenant_user = TenantUser.objects.filter(user=request.user).order_by("-id").first()
        if tenant_user:
            return "branding" in tenant_user.tenant.tier.features
        return False

class RequireInvoiceCustomizationPermission(BasePermission):
    def has_permission(self, request, view):
        tenant = getattr(request, "tenant", None)
        if tenant:
            return "invoice_customization" in tenant.tier.features
        tenant_user = TenantUser.objects.filter(user=request.user).order_by("-id").first()
        if tenant_user:
            return "invoice_customization" in tenant_user.tenant.tier.features
        return False

class IsTenantOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        tenant = obj.tenant if hasattr(obj, "tenant") else obj
        return TenantUser.objects.filter(tenant=tenant, user=request.user, role="owner").exists()

    def has_permission(self, request, view):
        if view.action == "create":
            tenant_id = request.data.get("tenant_id")
            if tenant_id:
                return TenantUser.objects.filter(
                    tenant_id=tenant_id, user=request.user, role="owner"
                ).exists()
        return True


class RoleBasedPermission(permissions.BasePermission):
    """
    Enforces RBAC using role_privileges mapping.
    Views can set required_privilege = "invoice:create" etc.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        required = getattr(view, "required_privilege", None)
        if not required:
            # If no specific privilege is required, allow safe methods
            return request.method in permissions.SAFE_METHODS

        # Check tenant role
        tenant_user = TenantUser.objects.filter(user=request.user).first()
        if tenant_user:
            role = tenant_user.role.lower().strip()
            allowed = role_privileges.get(role, [])
            return required in allowed

        # Check platform role
        platform_user = PlatformUser.objects.filter(user=request.user).first()
        if platform_user:
            role = platform_user.role.lower().strip()
            allowed = role_privileges.get(role, [])
            return required in allowed

        return False

    def has_object_permission(self, request, view, obj):
        # Default to same logic as has_permission
        return self.has_permission(request, view)


TENANT_ROLE_PRIVILEGES = {
    "owner": {"invoice:create", "invoice:update", "invoice:delete", "invoice:view"},
    "admin": {"invoice:view"},
    "manager": {"invoice:update", "invoice:view"},
    "user": {"invoice:create", "invoice:view"},
    "viewer": {"invoice:view"},
}

from rest_framework import permissions
from saas_app.core.models import TenantUser

TENANT_ROLE_PRIVILEGES = {
    "owner": {"invoice:create", "invoice:update", "invoice:delete", "invoice:view"},
    "admin": {"invoice:view"},
    "manager": {"invoice:update", "invoice:view"},
    "user": {"invoice:create", "invoice:view"},
    "viewer": {"invoice:view"},
}

from rest_framework import permissions
from saas_app.core.models import TenantUser
from saas_app.core.config.privileges import role_privileges

class TenantRequirePrivilegePermission(permissions.BasePermission):
    """
    Permission class that enforces RBAC privileges for tenant invoices.
    """

    def has_permission(self, request, view):
        required = getattr(view, "required_privilege", None)
        print(f"[DEBUG] Tenant Required privilege: {required}")

        if not required:
            print("[DEBUG] No required privilege set, allowing safe methods only")
            return request.method in permissions.SAFE_METHODS

        privileges = set()

        tenant = view.get_tenant()  # ✅ scope to current tenant
        tenant_user = TenantUser.objects.filter(user=request.user, tenant=tenant).first()
        if tenant_user:
            role_privs = set(role_privileges.get(tenant_user.role, []))
            privileges.update(role_privs)
            print(f"[DEBUG] TenantUser.role={tenant_user.role}, Privileges={role_privs}")
        else:
            print(f"[DEBUG] No TenantUser found for user {request.user.email} in tenant {tenant}")

        allowed = required in privileges
        print(f"[DEBUG] User: {request.user.email}, Required: {required}, Allowed: {allowed}")

        return allowed

class RequirePrivilegePermission(permissions.BasePermission):
    """
    Enforces RBAC using role_privileges mapping.
    Views can set required_privilege = "invoice:create" etc.
    """

   

ROLE_PRIVILEGES = {
    "platform_owner": {"invoice:create", "invoice:update", "invoice:delete", "invoice:view"},
    "platform_admin": {"invoice:view"},
    "platform_manager": {"invoice:update", "invoice:view"},
    "platform_user": {"invoice:create", "invoice:view"},
    "platform_viewer": {"invoice:view"},
}

class RequirePrivilegePermission(permissions.BasePermission):
    """
    Permission class that enforces RBAC privileges for platform invoices.
    """

    def has_permission(self, request, view):
        required = getattr(view, "required_privilege", None)
        print(f"[DEBUG] Required privilege: {required}")

        if not required:
            print("[DEBUG] No required privilege set, allowing safe methods only")
            return request.method in permissions.SAFE_METHODS

        privileges = set()

        # ✅ Only check platform role privileges for PlatformInvoiceViewSet
        platform_user = PlatformUser.objects.filter(user=request.user).first()
        if platform_user:
            role_privs = ROLE_PRIVILEGES.get(platform_user.role, set())
            privileges.update(role_privs)
            print(f"[DEBUG] Platform role: {platform_user.role}, Privileges: {role_privs}")

        allowed = required in privileges
        print(f"[DEBUG] User: {request.user.email}, Required: {required}, Allowed: {allowed}")

        return allowed
