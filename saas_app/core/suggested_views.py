import logging
import uuid
import time
import requests
import json
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django.db import connections
from django.db.utils import OperationalError
from django.core.cache import cache
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LogoutView
from django.views.decorators.csrf import csrf_exempt

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

# ✅ Corrected imports
from saas_app.accounts.models import CustomUser, Profile
from saas_app.core.models import Tenant, TenantUser, Tier, Location, Payment, TenantInvoice, PlatformInvoice, TenantCustomer, PlatformUser
from saas_app.core.forms import SignupForm, LoginForm
from saas_app.core.services.payments import initiate_paystack, verify_paystack, initiate_opay, verify_opay
from saas_app.core.utils.payments import create_payment, record_payment, verify_payment
from saas_app.core.utils.logging_helpers import log_json
from saas_app.core.utils.emails import send_invoice_email
from saas_app.core.utils.auth_helpers import is_tenant_owner, is_platform_owner, get_user_role

# Loggers
audit_logger = logging.getLogger("audit")
security_logger = logging.getLogger("security")

# -------------------
# Utility Functions
# -------------------
def get_client_ip(request):
    """Extract client IP address from request headers."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    return x_forwarded_for.split(",")[0] if x_forwarded_for else request.META.get("REMOTE_ADDR")

# -------------------
# Public Views
# -------------------
def landing_page_view(request):
    tiers = Tier.objects.all()
    return render(request, "core/landing.html", {"tiers": tiers})

def health_check(request):
    status = {"status": "ok"}
    try:
        connections["default"].cursor()
        status["database"] = "ok"
    except OperationalError:
        status["database"] = "error"

    try:
        cache.set("health_check_key", "test", timeout=5)
        status["cache"] = "ok" if cache.get("health_check_key") == "test" else "error"
    except Exception:
        status["cache"] = "error"

    if status["database"] != "ok" or status["cache"] != "ok":
        status["status"] = "error"
    return JsonResponse(status, status=200 if status["status"] == "ok" else 500)

def readiness_check(request):
    status = {"status": "ok"}
    try:
        connections["default"].cursor()
        status["database"] = "ok"
    except OperationalError:
        status["database"] = "error"

    try:
        cache.set("ready_check_key", "test", timeout=5)
        status["cache"] = "ok" if cache.get("ready_check_key") == "test" else "error"
    except Exception:
        status["cache"] = "error"

    if status["database"] != "ok" or status["cache"] != "ok":
        status["status"] = "error"
    return JsonResponse(status, status=200 if status["status"] == "ok" else 500)

# -------------------
# Auth Views
# -------------------
def signup_view(request):
    plan_param = request.GET.get("plan", "free")
    initial_data = {}
    if plan_param:
        try:
            tier = Tier.objects.get(name__iexact=plan_param.capitalize())
            initial_data["subscription_plan"] = tier.id
        except Tier.DoesNotExist:
            pass

    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            tenant = Tenant.objects.create(
                name=form.cleaned_data["company_name"],
                email=user.email,
                tier=form.cleaned_data["subscription_plan"]
            )
            TenantUser.objects.create(tenant=tenant, user=user, role="owner")
            login(request, user)
            return redirect("dashboard")
    else:
        form = SignupForm(initial=initial_data)
    return render(request, "core/signup.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            role = get_user_role(user)
            if role == "platform_owner":
                return redirect("platform_owner_dashboard")
            elif role == "tenant_owner":
                return redirect("owner_dashboard")
            elif role == "tenant_user":
                return redirect("dashboard")
            else:
                return redirect("dashboard")
        else:
            log_entry = {
                "event": "failed_login",
                "message": "failed login attempt",
                "user": request.POST.get("username"),
                "ip": request.META.get("REMOTE_ADDR"),
                "path": request.path,
            }
            log_json(security_logger, "warning", log_entry, request=request)
    else:
        form = LoginForm()
    return render(request, "core/login.html", {"form": form})

class CustomLogoutView(LogoutView):
    def get(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

# -------------------
# Dashboard
# -------------------
@login_required
def dashboard_view(request):
    user = request.user
    client_ip = get_client_ip(request)
    request_path = request.path
    http_method = request.method
    user_agent = request.META.get("HTTP_USER_AGENT", "unknown")
    correlation_id = str(uuid.uuid4())

    tenant_memberships = TenantUser.objects.filter(user=user).select_related("tenant")
    tenants = [membership.tenant for membership in tenant_memberships]
    invoices = TenantInvoice.objects.filter(tenant__in=tenants).order_by("-issued_at")
    payments = Payment.objects.filter(tenant__in=tenants).order_by("-created_at")

    platform_user = getattr(user, "platform_profile", None)

    if platform_user and platform_user.role == "platform_owner":
        tenants = Tenant.objects.all()
        invoices = TenantInvoice.objects.all().order_by("-issued_at")
        payments = Payment.objects.all().order_by("-created_at")
        audit_logger.info(json.dumps({
            "correlation_id": correlation_id,
            "timestamp": str(timezone.now()),
            "user": user.email,
            "role": platform_user.role,
            "action": "access",
            "scope": "ALL tenants, invoices, payments",
            "ip": client_ip,
            "path": request_path,
            "method": http_method,
            "user_agent": user_agent
        }))
    elif platform_user and platform_user.role == "platform_admin":
        tenants = Tenant.objects.all()
        invoices = []
        payments = []
        audit_logger.info(json.dumps({
            "correlation_id": correlation_id,
            "timestamp": str(timezone.now()),
            "user": user.email,
            "role": platform_user.role,
            "action": "access",
            "scope": "tenant metadata only",
            "restricted": ["invoices", "payments"],
            "ip": client_ip,
            "path": request_path,
            "method": http_method,
            "user_agent": user_agent
        }))
    elif tenant_memberships.exists():
        for membership in tenant_memberships:
            audit_logger.info(json.dumps({
                "correlation_id": correlation_id,
                "timestamp": str(timezone.now()),
                "user": user.email,
                "role": membership.role,
                "action": "access",
                "tenant": membership.tenant.name,
                "scope": "invoices and payments (scoped)",
                "ip": client_ip,
                "path": request_path,
                "method": http_method,
                "user_agent": user_agent
            }))
    else:
        messages.error(request, "You do not have access to the dashboard.")
        security_logger.warning(json.dumps({
            "correlation_id": correlation_id,
            "timestamp": str(timezone.now()),
            "user": user.email,
            "action": "unauthorized_access",
            "endpoint": request_path,
            "ip": client_ip,
            "method": http_method,
            "user_agent": user_agent
        }))
        return redirect("login")

    context = {
        "user": user,
        "memberships": tenant_memberships,
        "tenants": tenants,
        "invoices": invoices,
        "payments": payments,
        "correlation_id": correlation_id,
    }
    return render(request, "core/dashboard.html", context)

# -------------------
# Extra Views (added from skeleton)
# -------------------
@login_required
def platform_owner_dashboard(request):
    tenants = Tenant.objects.all()
    invoices = PlatformInvoice.objects.all().order_by("-created_at")
    return render(request, "core/platform_owner_dashboard.html", {
        "tenants": tenants,
        "invoices": invoices,
    })

@login_required
def tenant_reports(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)
    invoices = TenantInvoice.objects.filter(tenant=tenant)
    payments = Payment.objects.filter(tenant=tenant)
    return render

@login_required
def tenant_reports(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)
    invoices = TenantInvoice.objects.filter(tenant=tenant)
    payments = Payment.objects.filter(tenant=tenant)
    return render(request, "core/tenant_reports.html", {
        "tenant": tenant,
        "invoices": invoices,
        "payments": payments,
    })

@login_required
def global_reports(request):
    tenants = Tenant.objects.all()
    invoices = TenantInvoice.objects.all()
    payments = Payment.objects.all()
    return render(request, "core/global_reports.html", {
        "tenants": tenants,
        "invoices": invoices,
        "payments": payments,
    })
