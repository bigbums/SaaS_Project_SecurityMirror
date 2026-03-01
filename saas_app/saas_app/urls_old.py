# saas_app/urls.py
from django.contrib import admin
from django.urls import path, include
from accounts.views import signup
from rest_framework.routers import DefaultRouter
from saas_app.core.views import (
    CustomLogoutView,
    change_tier,
    generate_tenant_invoice,
    generate_platform_invoice,
    download_invoice,
    payment_history,
)

router = DefaultRouter()

urlpatterns = [
    # Core app routes
    path("", include("core.urls")),
    path("api/", include(router.urls)),

    # Logout route
    path("accounts/logout/", CustomLogoutView.as_view(next_page="landing_page"), name="logout"),
    path("accounts/", include("django.contrib.auth.urls")),

    # Admin site
    path("admin/", admin.site.urls),

    # Core routes for tenant management
    path("core/", include("core.urls")),
    path("signup/<int:tier_id>/", signup, name="signup"),
    path("tenant/<int:tenant_id>/change-tier/<int:tier_id>/", change_tier, name="change_tier"),
    path("tenant/<int:tenant_id>/payments/", payment_history, name="payment_history"),
    path("payment/<int:payment_id>/invoice/", download_invoice, name="download_invoice"),

    # Optional duplicate logout (remove if not needed)
    #path("logout/", CustomLogoutView.as_view(), name="logout"),

    path("accounts/", include("django.contrib.auth.urls")),

    # New invoice routes
    path("generate-tenant-invoice/", generate_tenant_invoice, name="generate_tenant_invoice"),
    path("generate-platform-invoice/", generate_platform_invoice, name="generate_platform_invoice"),
]
