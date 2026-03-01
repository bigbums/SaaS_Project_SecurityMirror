import logging
from django.http import HttpRequest
from saas_app.core.models import TenantUser, Tenant, PlatformUser

logger = logging.getLogger(__name__)

class TenantRequest(HttpRequest):
    """
    Custom HttpRequest type that includes a tenant attribute.
    This helps IDEs and type checkers know request.tenant is valid.
    """
    tenant: Tenant | None


class TenantMiddleware:
    """
    Middleware to attach the active tenant to the request.
    Assumes each authenticated user belongs to at least one tenant.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Always initialize tenant to None
        request.tenant = None

        if request.user and request.user.is_authenticated:
            # ✅ Check if user is a platform user first
            platform_user = PlatformUser.objects.filter(user=request.user).first()
            if platform_user:
                # Explicitly confirm platform users have no tenant
                request.tenant = None
                logger.debug(f"TenantMiddleware: platform user={request.user}, tenant=None")
                return self.get_response(request)

            # ✅ Otherwise, check tenant user
            tenant_user = TenantUser.objects.filter(user=request.user).order_by("-id").first()
            if tenant_user:
                request.tenant = tenant_user.tenant
                logger.debug(f"TenantMiddleware: tenant user={request.user}, tenant={tenant_user.tenant}")

        return self.get_response(request)
