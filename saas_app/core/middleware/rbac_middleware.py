import logging
from saas_app.core.models import TenantUser, PlatformUser
from saas_app.core.config.privileges import role_privileges  # ✅ use the same source as permissions.py

logger = logging.getLogger(__name__)

class RBACMiddleware:
    """
    Middleware to attach normalized RBAC permissions to request.user.
    Resolves role strictly from PlatformUser or TenantUser.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user and request.user.is_authenticated:
            role = None

            # ✅ Check PlatformUser first
            platform_user = PlatformUser.objects.filter(user=request.user).first()
            if platform_user:
                role = platform_user.role

            # ✅ If no platform role, check TenantUser
            tenant_user = None
            if hasattr(request, "tenant") and request.tenant:
                tenant_user = TenantUser.objects.filter(
                    user=request.user, tenant=request.tenant
                ).first()
            else:
                tenant_user = TenantUser.objects.filter(user=request.user).first()

            if tenant_user and not role:
                role = tenant_user.role

            # ✅ Normalize role name for consistency
            role = role.lower().strip() if role else None

            # ✅ Use role_privileges directly (not settings)
            permissions = []
            if role and role in role_privileges:
                permissions = list(set(role_privileges[role]))  # deduplicate

            # Attach to request.user
            request.user.permissions = permissions

            logger.debug(
                f"RBACMiddleware: user={request.user}, role={role}, permissions={permissions}"
            )

        return self.get_response(request)
