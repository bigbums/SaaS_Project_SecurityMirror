from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from saas_app.core.models import Tenant, TenantUser


def tenant_admin_required(view_func):
    """
    Decorator to ensure the logged-in user is an admin for the given tenant.
    Expects the view to receive tenant_id as a keyword argument.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        tenant_id = kwargs.get("tenant_id")
        tenant = get_object_or_404(Tenant, id=tenant_id)

        try:
            tenant_user = TenantUser.objects.get(tenant=tenant, user=request.user)
        except TenantUser.DoesNotExist:
            return HttpResponseForbidden("You do not belong to this tenant.")

        if tenant_user.role != "admin":
            return HttpResponseForbidden("You do not have permission to access this page.")

        # User is admin → proceed
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def tenant_role_required(allowed_roles=None):
    """
    Decorator to ensure the logged-in user has one of the allowed roles
    for the given tenant. Expects the view to receive tenant_id as a kwarg.
    """
    if allowed_roles is None:
        allowed_roles = ["admin"]  # default to admin-only

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            tenant_id = kwargs.get("tenant_id")
            tenant = get_object_or_404(Tenant, id=tenant_id)

            try:
                tenant_user = TenantUser.objects.get(tenant=tenant, user=request.user)
            except TenantUser.DoesNotExist:
                return HttpResponseForbidden("You do not belong to this tenant.")

            if tenant_user.role not in allowed_roles:
                return HttpResponseForbidden("You do not have permission to access this page.")

            return view_func(request, *args, **kwargs)

        return _wrapped_view
    return decorator

ROLE_GROUPS = {
    "elevated": ["admin", "supervisor", "team lead"],
    "management": ["manager"],
    "all_staff": ["admin", "supervisor", "team lead", "manager", "member"],
}

def tenant_role_required(allowed_roles=None):
    """
    Decorator to ensure the logged-in user has one of the allowed roles
    for the given tenant. Expects the view to receive tenant_id as a kwarg.
    allowed_roles can be:
      - a list of roles (["admin", "manager"])
      - a string key referencing ROLE_GROUPS ("elevated", "management")
    """
    if allowed_roles is None:
        allowed_roles = ["admin"]

    # If a group name is passed, expand it
    if isinstance(allowed_roles, str):
        allowed_roles = ROLE_GROUPS.get(allowed_roles, ["admin"])

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            tenant_id = kwargs.get("tenant_id")
            tenant = get_object_or_404(Tenant, id=tenant_id)

            try:
                tenant_user = TenantUser.objects.get(tenant=tenant, user=request.user)
            except TenantUser.DoesNotExist:
                return HttpResponseForbidden("You do not belong to this tenant.")

            if tenant_user.role not in allowed_roles:
                return HttpResponseForbidden("You do not have permission to access this page.")

            return view_func(request, *args, **kwargs)

        return _wrapped_view
    return decorator
