from django.contrib import admin
from django.urls import path, include
from accounts.views import signup
from saas_app.core.views import (
    CustomLogoutView, change_tier, generate_tenant_invoice,
    generate_platform_invoice, download_invoice, payment_history,
)

urlpatterns = [
    # Web routes
    path("", include("saas_app.urls")),

    # API routes (fix: include core/api_urls)
    path("api/v1/", include("saas_app.api_urls")),

    # Accounts
    path("accounts/logout/", CustomLogoutView.as_view(next_page="landing_page"), name="logout"),
    path("accounts/", include("django.contrib.auth.urls")),

    # Admin
    path("admin/", admin.site.urls),

    # Tenant/payment management
    path("signup/<int:tier_id>/", signup, name="signup"),
    path("tenant/<int:tenant_id>/change-tier/<int:tier_id>/", change_tier, name="change_tier"),
    path("tenant/<int:tenant_id>/payments/", payment_history, name="payment_history"),
    path("payment/<int:payment_id>/invoice/", download_invoice, name="download_invoice"),

    # Invoice generation
    path("generate-tenant-invoice/", generate_tenant_invoice, name="generate_tenant_invoice"),
    path("generate-platform-invoice/", generate_platform_invoice, name="generate_platform_invoice"),
]
