from core.models import TenantUser

class TenantMiddleware:
    """
    Middleware to attach the active tenant to the request.
    Assumes each user belongs to at least one tenant.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user and request.user.is_authenticated:
            tenant_user = (
                TenantUser.objects.filter(user=request.user)
                .order_by("-id")
                .first()
            )
            if tenant_user:
                request.tenant = tenant_user.tenant

        return self.get_response(request)
