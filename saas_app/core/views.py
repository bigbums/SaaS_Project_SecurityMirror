# Django imports
import logging

import uuid
import time
import requests
from datetime import timedelta

from django.conf import settings
from django.utils import timezone




from django.db import connections
from django.db.utils import OperationalError
from django.core.cache import cache
from django.db.models import Count

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader


from saas_app.accounts.models import CustomUser, Profile
from saas_app.core.models import TenantCustomer, PlatformUser, TenantInvoice, PlatformInvoice

from saas_app.core.utils.payments import create_payment, record_payment

from django.contrib.auth.decorators import login_required, user_passes_test

from saas_app.core.utils.payments import verify_payment

import json
from django.views.decorators.csrf import csrf_exempt

from core.utils.payments import record_payment

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView

# Models & Forms
from .models import Tenant, TenantUser, Tier, Location, Payment, TenantInvoice, PlatformInvoice
from saas_app.accounts.models import CustomUser, Profile
from .forms import SignupForm, LoginForm

# Services (high-level orchestration)
from saas_app.core.services.payments import initiate_paystack, verify_paystack, initiate_opay, verify_opay

# Utils (low-level helpers)
from saas_app.core.utils.payments import record_payment
from saas_app.core.utils.logging_helpers import log_json
from saas_app.core.utils.emails import send_invoice_email

# Auth helpers
#from utils.auth_helpers import get_user_role, role_required

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
    correlation_id = str(uuid.uuid4())
    tenant_memberships = TenantUser.objects.filter(user=user).select_related("tenant")
    tenants = [m.tenant for m in tenant_memberships]
    invoices = TenantInvoice.objects.filter(tenant__in=tenants).order_by("-issued_at")
    payments = Payment.objects.filter(tenant__in=tenants).order_by("-created_at")

    role = get_user_role(user)
    if role == "platform_owner":
        tenants = Tenant.objects.all()
        invoices = TenantInvoice.objects.all().order_by("-issued_at")
        payments = Payment.objects.all().order_by("-created_at")
    elif role == "platform_admin":
        tenants = Tenant.objects.all()
        invoices, payments = [], []

    elif role in ["tenant_owner", "tenant_user"]:
        # log per membership
        for m in tenant_memberships:
            audit_logger.info(json.dumps({
                "correlation_id": correlation_id,
                "timestamp": str(timezone.now()),
                "user": user.email,
                "role": m.role,
                "tenant": m.tenant.name,
                "action": "access",
                "scope": "tenant scoped invoices/payments"
            }))
    else:
        messages.error(request, "You do not have access to the dashboard.")
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



# Custom logout view
class CustomLogoutView(LogoutView):
    def get(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

# dashboard view

# Dedicated audit logger





audit_logger = logging.getLogger("audit")
security_logger = logging.getLogger("security")

def get_client_ip(request):
    """Helper to extract client IP address from request headers."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip

"""
Old Configuration

@login_required
def dashboard_view(request):
    user = request.user
    client_ip = get_client_ip(request)
    request_path = request.path
    http_method = request.method
    user_agent = request.META.get("HTTP_USER_AGENT", "unknown")

    # Generate a unique correlation ID for this request
    correlation_id = str(uuid.uuid4())

    # Tenant memberships for this user
    tenant_memberships = TenantUser.objects.filter(user=user).select_related("tenant")
    tenants = [membership.tenant for membership in tenant_memberships]

    # Default invoices/payments scoped to user's tenants
    invoices = TenantInvoice.objects.filter(tenant__in=tenants).order_by("-issued_at")
    payments = Payment.objects.filter(tenant__in=tenants).order_by("-created_at")
    

    # Role-based access enforcement
    if user.role == "PlatformGlobalAdmin":
        tenants = Tenant.objects.all()
        invoices = TenantInvoice.objects.all().order_by("-created_at")
        payments = Payment.objects.all().order_by("-created_at")

        audit_logger.info(json.dumps({
            "correlation_id": correlation_id,
            "timestamp": str(timezone.now()),
            "user": user.email,
            "role": user.role,
            "action": "access",
            "scope": "ALL tenants, invoices, payments",
            "ip": client_ip,
            "path": request_path,
            "method": http_method,
            "user_agent": user_agent
        }))

    elif user.role == "PlatformAdmin":
        tenants = Tenant.objects.all()
        invoices = []   # explicitly deny invoice visibility
        payments = []   # explicitly deny payment visibility

        audit_logger.info(json.dumps({
            "correlation_id": correlation_id,
            "timestamp": str(timezone.now()),
            "user": user.email,
            "role": user.role,
            "action": "access",
            "scope": "tenant metadata only",
            "restricted": ["invoices", "payments"],
            "ip": client_ip,
            "path": request_path,
            "method": http_method,
            "user_agent": user_agent
        }))

    elif user.role.startswith("Tenant"):
        # Log per membership for clarity
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
            "role": user.role,
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
        "correlation_id": correlation_id,  # optional: pass to template for debugging
    }

    return render(request, "core/dashboard.html", context)
"""

@login_required
def dashboard_view(request):
    user = request.user
    client_ip = get_client_ip(request)
    request_path = request.path
    http_method = request.method
    user_agent = request.META.get("HTTP_USER_AGENT", "unknown")

    # Generate a unique correlation ID for this request
    correlation_id = str(uuid.uuid4())

    # Tenant memberships for this user
    tenant_memberships = TenantUser.objects.filter(user=user).select_related("tenant")
    tenants = [membership.tenant for membership in tenant_memberships]

    # Default invoices/payments scoped to user's tenants
    invoices = TenantInvoice.objects.filter(tenant__in=tenants).order_by("-issued_at")
    payments = Payment.objects.filter(tenant__in=tenants).order_by("-created_at")

    # Role-based access enforcement
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
        invoices = []   # explicitly deny invoice visibility
        payments = []   # explicitly deny payment visibility

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
        # Log per membership for clarity
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
        "correlation_id": correlation_id,  # optional: pass to template for debugging
    }

    return render(request, "core/dashboard.html", context)


# @login_required
# def platform_dashboard_view(request):
#     tenants = Tenant.objects.all()
#     invoices = PlatformInvoice.objects.all().order_by("-created_at")
#     context = {
#         "user": request.user,
#         "tenants": tenants,
#         "invoices": invoices,
#     }
#     return render(request, "core/platform_dashboard.html", context)



def add_location(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)

    if not tenant.can_add_location():
        messages.error(request, f"{tenant.name} has reached the maximum number of locations ({tenant.tier.max_locations}).")
        return redirect("tenant_detail", tenant_id=tenant.id)

    if request.method == "POST":
        name = request.POST.get("name")
        address = request.POST.get("address", "")
        Location.objects.create(tenant=tenant, name=name, address=address)

        tenant.current_locations_count = tenant.locations.count()
        tenant.save()

        messages.success(request, f"Location {name} added successfully to {tenant.name}.")
        return redirect("tenant_detail", tenant_id=tenant.id)

    return render(request, "core/add_location.html", {"tenant": tenant})



def change_tier(request, tenant_id, tier_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)
    new_tier = get_object_or_404(Tier, id=tier_id)

    # Check if current usage fits within new tier limits
    if new_tier.max_users is not None and tenant.current_users_count > new_tier.max_users:
        messages.error(request, f"Cannot downgrade: {tenant.current_users_count} users exceed {new_tier.max_users} allowed.")
        return redirect("dashboard")

    if new_tier.max_locations is not None and tenant.current_locations_count > new_tier.max_locations:
        messages.error(request, f"Cannot downgrade: {tenant.current_locations_count} locations exceed {new_tier.max_locations} allowed.")
        return redirect("dashboard")

    tenant.tier = new_tier
    tenant.save()
    messages.success(request, f"{tenant.name} successfully moved to {new_tier.name} plan.")
    return redirect("dashboard")


#--------------------
# Payment Integration
#--------------------

# -----------
# Paystack
#------------



@login_required
def initiate_paystack_payment(request, tenant_id, tier_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)
    tier = get_object_or_404(Tier, id=tier_id)

    # Call the service layer
    auth_url = initiate_paystack(tenant, tier, request)
    if auth_url:
        return redirect(auth_url)
    messages.error(request, "Payment initialization failed.")
    return redirect("dashboard")

@login_required
def paystack_callback(request):
    ref = request.GET.get("reference")
    success = verify_paystack(ref)

    # Record payment outcome
    verify_payment(ref, "paystack", success)
    messages.success(request, "Payment successful!") if success else messages.error(request, "Payment failed.")
    return redirect("dashboard")

@login_required
def initiate_opay_payment(request, tenant_id, tier_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)
    tier = get_object_or_404(Tier, id=tier_id)

    # Call the service layer
    cashier_url = initiate_opay(tenant, tier, request)
    if cashier_url:
        return redirect(cashier_url)
    messages.error(request, "Opay payment initialization failed.")
    return redirect("dashboard")

@login_required
def opay_callback(request):
    ref = request.GET.get("reference")
    success = verify_opay(ref)

    # Record payment outcome
    verify_payment(ref, "opay", success)
    messages.success(request, "Payment successful!") if success else messages.error(request, "Payment failed.")
    return redirect("dashboard")




@login_required
def payment_history(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)
    payments = Payment.objects.filter(tenant=tenant).order_by("-created_at")

    return render(request, "payment_history.html", {
        "tenant": tenant,
        "payments": payments,
    })




def download_invoice(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="invoice_{payment.reference}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    p.setFont("Helvetica-Bold", 16)

    # --- Company Branding ---
    # Add logo (replace with your logo path)
    try:
        logo = ImageReader("static/images/logo.png")
        p.drawImage(logo, 50, 750, width=80, height=80)
    except:
        p.drawString(50, 800, "[Your SaaS Logo]")

    p.drawString(150, 800, "settings.PLATFORM_COMPANY_NAME")
    p.setFont("Helvetica", 10)
    p.drawString(150, 785, "www.yoursaas.com")
    p.drawString(150, 770, "support@yoursaas.com")
    p.drawString(150, 755, "+234 800 123 4567")
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 720, f"Invoice Number: {payment.invoice_number}")
    p.drawString(50, 700, f"Invoice Reference: {payment.reference}")


    p.line(50, 740, 550, 740)  # separator line

    # --- Invoice Details ---
    p.setFont("Helvetica", 12)
    p.drawString(50, 720, f"Invoice Reference: {payment.reference}")
    p.drawString(50, 700, f"Tenant: {payment.tenant.name}")
    p.drawString(50, 680, f"Tier: {payment.tier.name}")
    p.drawString(50, 660, f"Provider: {payment.provider.title()}")
    p.drawString(50, 640, f"Amount: ₦{payment.amount // 100}")
    p.drawString(50, 620, f"Status: {payment.status.title()}")
    p.drawString(50, 600, f"Date: {payment.created_at.strftime('%Y-%m-%d %H:%M')}")

    p.line(50, 580, 550, 580)

    # --- Footer ---
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(50, 560, "Thank you for your business!")
    p.drawString(50, 545, "This invoice serves as proof of payment.")

    p.showPage()
    p.save()

    return response

#---------------------------------
# Generate Tenant Customer Invoice
#---------------------------------
def generate_tenant_invoice(request):
    # Pick the first customer linked to the tenant of the current user
    customer = TenantCustomer.objects.filter(tenant__users__user=request.user).first()
    if not customer:
        return HttpResponse("No customer found for tenant.", status=400)

    invoice = TenantInvoice.objects.create(
        tenant=customer.tenant,
        customer=customer,
        amount=100,
        currency="NGN",
        status="pending"
    )

    # Queue email sending
    send_invoice_email.delay(request.user.email, invoice.id)
    return HttpResponse("Tenant invoice generated and email queued!")


#-----------------------------------
# Generate Platform Customer Invoice
#-----------------------------------

def generate_platform_invoice(request):
    # Pick the tenant linked to the current user
    tenant = Tenant.objects.filter(users__user=request.user).first()
    if not tenant:
        return HttpResponse("No tenant found for user.", status=400)

    invoice = PlatformInvoice.objects.create(
        tenant=tenant,
        amount=100,
        currency="USD",
        status="pending"
    )

    # Queue email sending
    send_invoice_email.delay(request.user.email, invoice.id)
    return HttpResponse("Platform invoice generated and email queued!")


#---------------------
# Paystack Webhook
#---------------------


@csrf_exempt
def paystack_webhook(request):
    """
    Handles Paystack webhook events.
    """
    try:
        payload = json.loads(request.body.decode("utf-8"))
        event = payload.get("event")
        data = payload.get("data", {})

        if event == "charge.success":
            reference = data.get("reference")
            amount = data.get("amount") / 100  # Paystack sends amount in kobo
            email = data.get("customer", {}).get("email")

            # Try to find the invoice by reference
            invoice = None
            try:
                invoice = TenantInvoice.objects.get(audit_log_id=reference)
            except TenantInvoice.DoesNotExist:
                try:
                    invoice = PlatformInvoice.objects.get(audit_log_id=reference)
                except PlatformInvoice.DoesNotExist:
                    pass

            if invoice:
                record_payment(
                    invoice=invoice,
                    amount=amount,
                    method="paystack",
                    transaction_id=reference,
                    receipt_number=f"PSK-{reference}",
                )
                return JsonResponse({"status": "success"})

        return JsonResponse({"status": "ignored"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)



#--------------------------------------------
# Paystack Initialization Tenant Payment View
#--------------------------------------------

def tenant_paystack_payment(request, invoice_id):
    """
    Initializes a Paystack payment for a tenant invoice.
    """
    invoice = get_object_or_404(TenantInvoice, id=invoice_id)
    user = request.user
    amount = invoice.amount  # or request.POST.get("amount")

    try:
        auth_url, payment = create_payment(user=user, invoice=invoice, amount=amount)
        return JsonResponse({"status": "success", "authorization_url": auth_url, "payment_id": payment.id})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


#----------------------------------------------
# Paystack Initialization Platform Payment View
#----------------------------------------------

def platform_paystack_payment(request, invoice_id):
    """
    Initializes a Paystack payment for a platform invoice.
    """
    invoice = get_object_or_404(PlatformInvoice, id=invoice_id)
    user = request.user
    amount = invoice.amount

    try:
        auth_url, payment = create_payment(user=user, invoice=invoice, amount=amount)
        return JsonResponse({"status": "success", "authorization_url": auth_url, "payment_id": payment.id})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)



def paystack_success(request):
    """
    Page shown when Paystack redirects after a successful payment.
    Note: Actual confirmation is handled by webhook.
    """
    return render(request, "payments/success.html")

def paystack_failure(request):
    """
    Page shown when Paystack redirects after a failed/cancelled payment.
    """
    return render(request, "payments/failure.html")


@csrf_exempt
def init_paystack_payment(request, invoice_id):
    # Call Paystack API, return authorization_url
    return JsonResponse({"status": "success", "authorization_url": "https://paystack.com/checkout/..."})

@csrf_exempt
def init_opay_payment(request, invoice_id):
    # Call Opay API, return authorization_url
    return JsonResponse({"status": "success", "authorization_url": "https://opay.com/checkout/..."})


# ------------------------------------------
# Tenant Invoice Payment Endpoints / Options
# ------------------------------------------


@csrf_exempt
def mark_tenant_invoice_paid(request, invoice_id):
    """Cash payment: mark tenant invoice as paid immediately."""
    invoice = get_object_or_404(TenantInvoice, id=invoice_id)
    invoice.status = "paid"
    invoice.payment_method = "cash"
    invoice.save()
    return JsonResponse({
        "status": "success",
        "invoice_id": invoice.id,
        "tenant_id": invoice.tenant.id,
        "tenant_name": invoice.tenant_name,   # ✅ snapshot field
        "customer_id": invoice.customer.id,
        "amount": str(invoice.amount),
        "currency": invoice.currency,
        "status_value": invoice.status,
    })


@csrf_exempt
def record_tenant_teller_payment(request, invoice_id):
    """Teller payment: mark tenant invoice as pending teller confirmation."""
    invoice = get_object_or_404(TenantInvoice, id=invoice_id)
    invoice.status = "pending"
    invoice.payment_method = "teller"
    invoice.save()
    return JsonResponse({
        "status": "success",
        "message": "Awaiting teller confirmation",
        "invoice_id": invoice.id,
        "tenant_id": invoice.tenant.id,
        "tenant_name": invoice.tenant_name,   # ✅ snapshot field
    })


@csrf_exempt
def record_tenant_bank_transfer(request, invoice_id):
    """Bank transfer: mark tenant invoice as pending bank confirmation."""
    invoice = get_object_or_404(TenantInvoice, id=invoice_id)
    invoice.status = "pending"
    invoice.payment_method = "bank_transfer"
    invoice.save()
    return JsonResponse({
        "status": "success",
        "message": "Awaiting bank confirmation",
        "invoice_id": invoice.id,
        "tenant_id": invoice.tenant.id,
        "tenant_name": invoice.tenant_name,   # ✅ snapshot field
    })


@csrf_exempt
def tenant_paystack_payment(request, invoice_id):
    """Initialize Paystack payment for tenant invoice."""
    invoice = get_object_or_404(TenantInvoice, id=invoice_id)
    user = request.user
    amount = invoice.amount
    try:
        auth_url, payment = create_payment(user=user, invoice=invoice, amount=amount)
        return JsonResponse({
            "status": "success",
            "authorization_url": auth_url,
            "payment_id": payment.id,
            "invoice_id": invoice.id,
            "tenant_id": invoice.tenant.id,
            "tenant_name": invoice.tenant_name,   # ✅ snapshot field
        })
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


@csrf_exempt
def tenant_opay_payment(request, invoice_id):
    """Initialize Opay payment for tenant invoice."""
    invoice = get_object_or_404(TenantInvoice, id=invoice_id)
    user = request.user
    amount = invoice.amount
    try:
        auth_url, payment = create_payment(user=user, invoice=invoice, amount=amount, provider="opay")
        return JsonResponse({
            "status": "success",
            "authorization_url": auth_url,
            "payment_id": payment.id,
            "invoice_id": invoice.id,
            "tenant_id": invoice.tenant.id,
            "tenant_name": invoice.tenant_name,   # ✅ snapshot field
        })
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


# --------------------------------------------
# Platform Invoice Payment Endpoints / Options
# --------------------------------------------

@csrf_exempt
def mark_platform_invoice_paid(request, invoice_id):
    """Cash payment: mark platform invoice as paid immediately."""
    invoice = get_object_or_404(PlatformInvoice, id=invoice_id)
    invoice.status = "paid"
    invoice.payment_method = "cash"
    invoice.save()
    return JsonResponse({
        "status": "success",
        "invoice_id": invoice.id,
        "tenant_id": invoice.tenant.id,
        "tenant_name": invoice.tenant.name,   # ✅ tenant linked to platform invoice
        "platform_name": "settings.PLATFORM_COMPANY_NAME",  # ✅ explicit platform identity
        "amount": str(invoice.amount),
        "currency": invoice.currency,
        "status_value": invoice.status,
    })


@csrf_exempt
def record_platform_teller_payment(request, invoice_id):
    """Teller payment: mark platform invoice as pending teller confirmation."""
    invoice = get_object_or_404(PlatformInvoice, id=invoice_id)
    invoice.status = "pending"
    invoice.payment_method = "teller"
    invoice.save()
    return JsonResponse({
        "status": "success",
        "message": "Awaiting teller confirmation",
        "invoice_id": invoice.id,
        "tenant_id": invoice.tenant.id,
        "tenant_name": invoice.tenant.name,
        "platform_name": "settings.PLATFORM_COMPANY_NAME",  # ✅ branding
    })


@csrf_exempt
def record_platform_bank_transfer(request, invoice_id):
    """Bank transfer: mark platform invoice as pending bank confirmation."""
    invoice = get_object_or_404(PlatformInvoice, id=invoice_id)
    invoice.status = "pending"
    invoice.payment_method = "bank_transfer"
    invoice.save()
    return JsonResponse({
        "status": "success",
        "message": "Awaiting bank confirmation",
        "invoice_id": invoice.id,
        "tenant_id": invoice.tenant.id,
        "tenant_name": invoice.tenant.name,
        "platform_name": "settings.PLATFORM_COMPANY_NAME",  # ✅ branding
    })


@csrf_exempt
def platform_paystack_payment(request, invoice_id):
    """Initialize Paystack payment for platform invoice."""
    invoice = get_object_or_404(PlatformInvoice, id=invoice_id)
    user = request.user
    amount = invoice.amount
    try:
        auth_url, payment = create_payment(user=user, invoice=invoice, amount=amount)
        return JsonResponse({
            "status": "success",
            "authorization_url": auth_url,
            "payment_id": payment.id,
            "invoice_id": invoice.id,
            "tenant_id": invoice.tenant.id,
            "tenant_name": invoice.tenant.name,
            "platform_name": "settings.PLATFORM_COMPANY_NAME",  # ✅ branding
        })
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


@csrf_exempt
def platform_opay_payment(request, invoice_id):
    """Initialize Opay payment for platform invoice."""
    invoice = get_object_or_404(PlatformInvoice, id=invoice_id)
    user = request.user
    amount = invoice.amount
    try:
        auth_url, payment = create_payment(user=user, invoice=invoice, amount=amount, provider="opay")
        from django.conf import settings
        return JsonResponse({
            "status": "success",
            "authorization_url": auth_url,
            "payment_id": payment.id,
            "invoice_id": invoice.id,
            "tenant_id": invoice.tenant.id,
            "tenant_name": invoice.tenant.name,
            "platform_name": settings.PLATFORM_COMPANY_NAME,  # ✅ "Bumys Cloud"
        })
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


# Role Checks

def is_platform_admin(user):
    return hasattr(user, "platformuser") and user.platformuser.role == "platform_admin"

def is_owner(user):
    return hasattr(user, "tenantuser") and user.tenantuser.role == "owner"

def is_manager(user):
    return hasattr(user, "tenantuser") and user.tenantuser.role == "manager"


# Protected Dashboards
@login_required
@user_passes_test(is_platform_admin)
def platform_dashboard(request):
    return render(request, "dashboard/platform.html")

# Tenant Owner Dashboard
@login_required
@user_passes_test(is_owner)
def owner_dashboard(request):
    tenant_user = request.tenantuser
    tenant = tenant_user.tenant
    users = TenantUser.objects.filter(tenant=tenant)
    online_count = users.filter(user__is_active=True).count()

    context = {
        "tenant": tenant,
        "users": users,
        "online_count": online_count,
        "is_platform_owner": False,  # flag for template
    }
    return render(request, "dashboard/tenant_owner.html", context)



@login_required
@user_passes_test(is_manager)
def manager_dashboard(request):
    return render(request, "dashboard/manager.html")

"""
Commented out for duplication in auth_helpers.py
def is_platform_owner(user):
    return hasattr(user, "platformuser") and user.platformuser.role == "platform_owner"
"""
@login_required
@user_passes_test(is_platform_owner)
def platform_owner_dashboard(request):
    tenants = Tenant.objects.all()
    if get_user_role(request.user) != "platform_owner":
        return HttpResponseForbidden("Access denied")

    # Handle filters
    status = request.GET.get("status")
    platform_users = PlatformUser.objects.all()
    if status == "active":
        platform_users = platform_users.filter(user__is_active=True)
    elif status == "inactive":
        platform_users = platform_users.filter(user__is_active=False)

    # Counts for overview
    active_platform_users = PlatformUser.objects.filter(user__is_active=True).count()
    inactive_platform_users = PlatformUser.objects.filter(user__is_active=False).count()

    tenant_users = TenantUser.objects.all()
    active_tenant_users = tenant_users.filter(user__is_active=True).count()
    inactive_tenant_users = tenant_users.filter(user__is_active=False).count()

    context = {
        "tenants": tenants,
        "platform_users": platform_users,
        "status": status,
        "active_platform_users": active_platform_users,
        "inactive_platform_users": inactive_platform_users,
        "active_tenant_users": active_tenant_users,
        "inactive_tenant_users": inactive_tenant_users,
    }
    return render(request, "dashboard/platform_owner.html", context)


@login_required
@user_passes_test(is_platform_owner)
def platform_tenant_detail(request, tenant_id):
    tenant = Tenant.objects.get(id=tenant_id)
    users = TenantUser.objects.filter(tenant=tenant)

    # Count online users
    online_count = users.filter(user__is_active=True).count()

    context = {
        "tenant": tenant,
        "users": users,
        "online_count": online_count,
        "is_platform_owner": True,  # flag for template
    }
    return render(request, "dashboard/tenant_owner.html", context)


# Platform and Tenant Reports
def global_reports(request):
    tenants = Tenant.objects.all()

    # Example: count logins per day for last 7 days
    today = timezone.now().date()
    login_data = []
    labels = []
    for i in range(7):
        day = today - timedelta(days=i)
        labels.append(day.strftime("%Y-%m-%d"))
        count = PlatformUser.objects.filter(last_login__date=day).count()
        login_data.append(count)

    context = {
        "tenants": tenants,
        "active_tenant_users": TenantUser.objects.filter(user__is_active=True).count(),
        "inactive_tenant_users": TenantUser.objects.filter(user__is_active=False).count(),
        "active_platform_users": PlatformUser.objects.filter(user__is_active=True).count(),
        "inactive_platform_users": PlatformUser.objects.filter(user__is_active=False).count(),
        "login_labels": labels[::-1],   # reverse to chronological order
        "login_counts": login_data[::-1],
    }
    return render(request, "dashboard/global_reports.html", context)



@login_required
@user_passes_test(is_tenant_owner)
def tenant_reports(request, tenant_id):
    role = get_user_role(request.user)
    if role not in ["tenant_owner", "platform_owner"]:
        return HttpResponseForbidden("Access denied")
    tenant = Tenant.objects.get(id=tenant_id)
    users = TenantUser.objects.filter(tenant=tenant)
    

    # Active/inactive counts
    active_users = users.filter(user__is_active=True).count()
    inactive_users = users.filter(user__is_active=False).count()

    # Login activity for last 7 days
    today = timezone.now().date()
    login_labels = []
    login_counts = []
    for i in range(7):
        day = today - timedelta(days=i)
        login_labels.append(day.strftime("%Y-%m-%d"))
        count = users.filter(user__last_login__date=day).count()
        login_counts.append(count)

    context = {
        "tenant": tenant,
        "users": users,
        "active_users": active_users,
        "inactive_users": inactive_users,
        "login_labels": login_labels[::-1],   # chronological order
        "login_counts": login_counts[::-1],
        "is_platform_owner": False,  # or True if platform owner is viewing
    }
    return render(request, "dashboard/tenant_reports.html", context)

from django.http import JsonResponse

def projects(request):
    # Temporary placeholder response
    return JsonResponse({"message": "Projects endpoint works!"})


#-----------------------------------------------
# Diagnostic View to Confirm Middleware Behavior
#-----------------------------------------------

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(["GET"])
@permission_classes([AllowAny])  # allow anyone to hit this endpoint
def diagnostic_view(request):
    """
    Diagnostic endpoint to confirm TenantMiddleware and RBACMiddleware behavior.
    """
    data = {
        "user": str(request.user) if request.user.is_authenticated else "Anonymous",
        "role": getattr(request.user, "role", None),
        "permissions": getattr(request.user, "permissions", []),
        "tenant": str(getattr(request, "tenant", None)),
    }
    return Response(data)
