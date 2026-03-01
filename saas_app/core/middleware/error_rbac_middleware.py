import logging
from django.conf import settings
from saas_app.core.models import TenantUser, PlatformUser

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
            if hasattr(request, "tenant"):
                tenant_user = TenantUser.objects.filter(
                    user=request.user, tenant=request.tenant
                ).first()
            else:
                # fallback: just pick the first tenant_user for this user
                tenant_user = TenantUser.objects.filter(user=request.user).first()

            if tenant_user and not role:
                role = tenant_user.role

            # ✅ Do NOT fall back to request.user.role
            # This avoids defaulting to "owner" from CustomUser

            permissions = []

            # Merge privileges from Python dict
            if role and role in getattr(settings, "ROLE_PRIVILEGES", {}):
                permissions.extend(settings.ROLE_PRIVILEGES[role])

            """
            # Merge privileges from roles.json
            if role and role in getattr(settings, "ROLES_CONFIG", {}):
                role_config = settings.ROLES_CONFIG[role]
                for resource, actions in role_config.items():
                    for action in actions:
                        permissions.append(f"{resource}:{action}")

                        """
                        
            # Attach permissions to user
            request.user.permissions = permissions

            logger.debug(
                f"RBACMiddleware: user={request.user}, role={role}, permissions={permissions}"
            )
            logger.debug(
                f"TenantUser queryset: {TenantUser.objects.filter(user=request.user)}"
            )

        return self.get_response(request)
