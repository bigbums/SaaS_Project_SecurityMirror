from functools import wraps
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required


def is_tenant_owner(user):
    """
    Returns True if the user is a tenant owner.
    """
    from saas_app.core.models import TenantUser  # local import to avoid circular dependency
    return TenantUser.objects.filter(user=user, role="owner").exists()


def is_platform_owner(user):
    """
    Returns True if the user is a platform owner.
    """
    from saas_app.core.models import PlatformUser  # local import to avoid circular dependency
    return PlatformUser.objects.filter(user=user, role="platform_owner").exists()


def get_user_role(user):
    """
    Returns the role of the user as a string:
    - "platform_owner"
    - "tenant_owner"
    - "tenant_user"
    - "unknown" if no role found
    """
    from saas_app.core.models import PlatformUser, TenantUser  # local import

    try:
        platform_user = PlatformUser.objects.get(user=user)
        if platform_user.role == "platform_owner":
            return "platform_owner"
    except PlatformUser.DoesNotExist:
        pass

    try:
        tenant_user = TenantUser.objects.get(user=user)
        if tenant_user.role == "owner":
            return "tenant_owner"
        else:
            return "tenant_user"
    except TenantUser.DoesNotExist:
        pass

    return "unknown"


def role_required(required_roles):
    """
    Decorator to restrict access based on user role(s).
    Usage:
        @role_required("platform_owner")
        @role_required(["platform_owner", "tenant_owner"])
    """
    if isinstance(required_roles, str):
        required_roles = [required_roles]

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if get_user_role(request.user) not in required_roles:
                return HttpResponseForbidden("Access denied")
            return view_func(request, *args, **kwargs)
        return _wrapped_view

    return decorator
