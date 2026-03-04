from rest_framework.routers import DefaultRouter
from saas_app.core.viewsets import (
    UserViewSet,
    ItemViewSet,
    SaleViewSet,
    SaleItemViewSet,
    TenantCustomerViewSet,
    TenantInvoiceViewSet,
    TenantPaymentViewSet,
    TenantViewSet,
    TenantUserViewSet,
    PlatformInvoiceViewSet,
)

router = DefaultRouter()

# Core viewsets
router.register("users", UserViewSet, basename="user")
router.register("tenants", TenantViewSet, basename="tenant")
router.register("tenant-users", TenantUserViewSet, basename="tenantuser")
router.register("items", ItemViewSet, basename="item")
router.register("sales", SaleViewSet, basename="sale")
router.register("sale-items", SaleItemViewSet, basename="saleitem")
router.register("tenant-customers", TenantCustomerViewSet, basename="tenantcustomer")
router.register("tenant-invoices", TenantInvoiceViewSet, basename="tenantinvoice")
router.register("tenant-payments", TenantPaymentViewSet, basename="tenantpayment")

# Platform invoices — ✅ this line ensures /api/platform-invoices/{id}/mark_paid/ works
router.register("platform-invoices", PlatformInvoiceViewSet, basename="platforminvoice")

app_name = "v1"
urlpatterns = router.urls
