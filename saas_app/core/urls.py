from django.contrib import admin
from django.urls import path, include
from accounts.views import signup
from saas_app.core.views import (
    CustomLogoutView, change_tier, generate_tenant_invoice,
    generate_platform_invoice, download_invoice, payment_history,
    landing_page_view, health_check, readiness_check,
    signup_view, login_view, dashboard_view,
    platform_owner_dashboard, platform_tenant_detail,
    global_reports, tenant_reports,
    paystack_webhook, paystack_success, paystack_failure,
)

urlpatterns = [
    # Web routes
    path("", landing_page_view, name="landing"),
    path("health/", health_check, name="health_check"),
    path("ready/", readiness_check, name="readiness_check"),
    path("signup/", signup_view, name="signup"),
    path("accounts/login/", login_view, name="login"),
    path("accounts/logout/", CustomLogoutView.as_view(next_page="landing_page"), name="logout"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),

    # Dashboard
    path("dashboard/", dashboard_view, name="dashboard"),
    path("dashboard/platform-owner/", platform_owner_dashboard, name="platform_owner_dashboard"),
    path("dashboard/platform-owner/<int:tenant_id>/", platform_tenant_detail, name="platform_tenant_detail"),
    path("dashboard/reports/", global_reports, name="reports"),
    path("dashboard/tenant/<int:tenant_id>/reports/", tenant_reports, name="tenant_reports"),

    # Payment callbacks
    path("webhooks/paystack/", paystack_webhook, name="paystack_webhook"),
    path("payments/success/", paystack_success, name="paystack_success"),
    path("payments/failure/", paystack_failure, name="paystack_failure"),

    # API routes (fix: point to saas_app/api_urls)
    # path("api/v1/", include("saas_app.api_urls")),

    # Accounts
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
