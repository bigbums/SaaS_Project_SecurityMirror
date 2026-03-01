# saas_app/core/permissions.py
from rest_framework import permissions
from rest_framework.permissions import BasePermission
from saas_app.core.utils.features import has_feature
from saas_app.core.models import Tenant, TenantUser

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


    from rest_framework import permissions
from saas_app.core.models import TenantUser

class RoleBasedPermission(permissions.BasePermission):
    """
    Enforces RBAC:
    - Owners and managers: full access
    - Members: read-only (SAFE_METHODS)
    - Anonymous: denied
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        tenant_user = TenantUser.objects.filter(user=request.user).first()
        if not tenant_user:
            return False

        role = tenant_user.role

        if role in ["owner", "manager"]:
            return True

        if role == "member":
            # Members can only perform safe methods (GET, HEAD, OPTIONS)
            return request.method in permissions.SAFE_METHODS

        return False


    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Tenant):
            return TenantUser.objects.filter(tenant=obj, user=request.user, role="owner").exists()
        if isinstance(obj, TenantUser):
            return TenantUser.objects.filter(tenant=obj.tenant, user=request.user, role="owner").exists()
        return request.method in permissions.SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Tenant):
            return TenantUser.objects.filter(tenant=obj, user=request.user, role="owner").exists()
        if isinstance(obj, TenantUser):
            return TenantUser.objects.filter(tenant=obj.tenant, user=request.user, role="owner").exists()
        return request.method in permissions.SAFE_METHODS



class RequirePrivilegePermission(BasePermission):
    def has_permission(self, request, view):
        required = getattr(view, "required_privilege", None)
        if not required:
            return True
        resource, action = required.split(":")
        return (
            request.user.is_authenticated
            and hasattr(request.user, "permissions")
            and f"{resource}:{action}" in request.user.permissions
        )
