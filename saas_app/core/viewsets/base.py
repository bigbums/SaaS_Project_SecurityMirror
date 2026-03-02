# saas_app/core/viewsets/base.py
from rest_framework import viewsets
from saas_app.core.permissions import RoleBasedPermission
from saas_app.core.models import TenantUser

class BaseTenantViewSet(viewsets.ModelViewSet):
    """
    Base viewset that scopes queries to the authenticated user's tenants
    and automatically attaches tenant on create.
    """
    permission_classes = [RoleBasedPermission]

    def get_queryset(self):
        # Collect all tenant IDs linked to the authenticated user
        tenant_ids = TenantUser.objects.filter(
            user=self.request.user
        ).values_list("tenant_id", flat=True)

        # Scope queryset to those tenants
        return self.queryset.filter(id__in=tenant_ids)

    def perform_create(self, serializer):
        # Attach tenant automatically (first tenant if multiple)
        tenant_user = TenantUser.objects.filter(user=self.request.user).first()
        if tenant_user:
            # Save with tenant; do not force user field unless model requires it
            serializer.save(tenant=tenant_user.tenant)
        else:
            raise PermissionError("User is not linked to any tenant")
