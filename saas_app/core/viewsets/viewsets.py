from rest_framework import viewsets, permissions
from rest_framework.response import Response
from django.utils import timezone
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import io
import uuid


from saas_app.core.permissions import IsTenantOwner, RoleBasedPermission, RequirePrivilegePermission, TenantRequirePrivilegePermission
from saas_app.core.viewsets.base import BaseTenantViewSet
from saas_app.core.models import (
    Sale, SaleItem, Item, TenantCustomer, TenantInvoice, Tier, Location, Payment, TenantInvoice, 
    PlatformInvoice, TenantPayment, Tenant, TenantUser, User, PlatformUser
)
from saas_app.core.serializers import (
    SaleSerializer, SaleItemSerializer, UserSerializer,
    ItemSerializer, TenantCustomerSerializer, TenantInvoiceSerializer,
    TenantPaymentSerializer, TenantSerializer, TenantUserSerializer, PlatformInvoiceSerializer
)

from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from audit.utils import log_invoice_action

from rest_framework import viewsets, status

from rest_framework.response import Response
from django.utils import timezone

from saas_app.core.constants import INVOICE_STATUS_CHOICES

from saas_app.core.invoice_actions import (
    MarkPaidSerializer,
    MarkRefundedSerializer,
    DownloadPDFSerializer,
    SendReminderSerializer,
)



from saas_app.core.utils.logging_helpers import log_invoice_action

from saas_app.core.viewsets.base_invoice_viewset import BaseInvoiceViewSet

# Main serializers
from saas_app.core.serializers import PlatformInvoiceSerializer

 



User = get_user_model()






class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer



class SaleViewSet(BaseTenantViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer

    def perform_create(self, serializer):
        tenant_user = TenantUser.objects.filter(user=self.request.user).first()
        tenant = tenant_user.tenant
        user = self.request.user
        sale = serializer.save(tenant=tenant, user=user)

        # Calculate total amount
        total = sum(item.line_total for item in sale.items.all())
        sale.total_amount = total
        sale.save()

        # Decide invoice type based on context
        if tenant.tier:  # Example condition: tenant-level sale
            invoice = TenantInvoice.objects.create(
                tenant=tenant,
                customer=None,  # link to TenantCustomer if available
                amount=total,
                currency="NGN",
                status="paid",
                due_date=timezone.now().date(),
            )
            invoice_type = "tenant_invoice"
        else:  # Example condition: platform-level sale
            invoice = PlatformInvoice.objects.create(
                tenant=tenant,
                amount=total,
                currency="USD",
                status="paid",
                due_date=timezone.now().date(),
            )
            invoice_type = "platform_invoice"

        # --- PDF Invoice Generation ---
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        p.setFont("Helvetica-Bold", 16)

        try:
            logo = ImageReader("static/images/logo.png")
            p.drawImage(logo, 50, 750, width=80, height=80)
        except:
            p.drawString(50, 800, "[Company Logo]")

        p.drawString(150, 800, f"{tenant.name} Invoice")
        p.setFont("Helvetica", 12)
        p.drawString(50, 720, f"Invoice ID: {invoice.id}")
        p.drawString(50, 700, f"Sale Invoice Number: {sale.invoice_number}")
        p.drawString(50, 680, f"Tenant: {tenant.name}")
        p.drawString(50, 660, f"Amount: {total}")
        p.drawString(50, 640, f"Date: {timezone.now().strftime('%Y-%m-%d')}")
        p.showPage()
        p.save()

        buffer.seek(0)
        invoice.pdf_file.save(f"{invoice_type}_{sale.invoice_number}.pdf", buffer, save=True)

        # Link invoice to sale
        sale.invoice = invoice
        sale.save()

        # Audit logging
        log_invoice_action(invoice, action="sale_invoice_created", performed_by=user)


class SaleItemViewSet(BaseTenantViewSet):
    queryset = SaleItem.objects.all()
    serializer_class = SaleItemSerializer

    def get_queryset(self):
        tenant_ids = TenantUser.objects.filter(user=self.request.user).values_list("tenant_id", flat=True)
        return SaleItem.objects.filter(sale__tenant_id__in=tenant_ids)

    def perform_create(self, serializer):
        sale_id = self.request.data.get("sale")
        item_id = self.request.data.get("item")
        quantity = int(self.request.data.get("quantity", 1))

        item = Item.objects.get(id=item_id)
        line_total = item.price * quantity

        # Deduct stock for products
        if item.type == "product":
            if item.stock < quantity:
                raise ValueError("Insufficient stock for product")
            item.stock -= quantity
            item.save()

        serializer.save(sale_id=sale_id, item=item, quantity=quantity, line_total=line_total)


class ItemViewSet(BaseTenantViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def get_queryset(self):
        tenant_ids = TenantUser.objects.filter(user=self.request.user).values_list("tenant_id", flat=True)
        return Item.objects.filter(tenant_id__in=tenant_ids)


class TenantCustomerViewSet(BaseTenantViewSet):
    queryset = TenantCustomer.objects.all()
    serializer_class = TenantCustomerSerializer


import uuid
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.response import Response
from saas_app.core.models import Tenant, TenantCustomer, TenantUser, TenantInvoice
from audit.utils import log_invoice_action
from saas_app.core.permissions import TenantRequirePrivilegePermission
from saas_app.core.serializers import TenantInvoiceSerializer

class TenantInvoiceViewSet(viewsets.ModelViewSet):
    queryset = TenantInvoice.objects.all()
    serializer_class = TenantInvoiceSerializer
    permission_classes = [TenantRequirePrivilegePermission]
    basename = "tenant"

    action_privileges = {
        "list": "invoice:view",
        "retrieve": "invoice:view",
        "create": "invoice:create",
        "update": "invoice:update",
        "partial_update": "invoice:update",
        "destroy": "invoice:delete",
        "mark_paid": "invoice:update",
        "mark_overdue": "invoice:update",
        "mark_refunded": "invoice:update",
        "download_pdf": "invoice:download_pdf",
        "send_reminder": "invoice:send_reminder",
    }

    def get_required_privilege(self):
        return self.action_privileges.get(self.action)

    def get_permissions(self):
        required = self.get_required_privilege()
        setattr(self, "required_privilege", required)
        print(f"[DEBUG] Setting required_privilege='{required}' for action='{self.action}' (TenantInvoiceViewSet)")
        return [TenantRequirePrivilegePermission()]

    def get_tenant(self):
        tenant_id = self.kwargs.get("tenant_id")
        if tenant_id:
            return Tenant.objects.get(id=tenant_id)

        if "pk" in self.kwargs:
            invoice_id = self.kwargs["pk"]
            invoice = TenantInvoice.objects.filter(id=invoice_id).first()
            if invoice:
                return invoice.tenant

        tenant_user = TenantUser.objects.filter(user=self.request.user).first()
        return tenant_user.tenant if tenant_user else None

    def get_queryset(self):
        tenant = self.get_tenant()
        return TenantInvoice.objects.filter(tenant=tenant)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        customer_id = request.data.get("customer")
        if not customer_id:
            return Response({"error": "customer is required"}, status=status.HTTP_400_BAD_REQUEST)
        customer = TenantCustomer.objects.get(id=customer_id)

        audit_id = request.data.get("audit_log_id") or str(uuid.uuid4())
        tenant = self.get_tenant()

        invoice = serializer.save(
            tenant=tenant,
            customer=customer,
            issued_at=timezone.now(),
            status=request.data.get("status", "unpaid"),
            description=request.data.get("description", "Invoice generated"),
            pdf_file=None,
            audit_log_id=audit_id
        )

        log_invoice_action(invoice, action="tenant_invoice_created", performed_by=request.user)
        print(f"[DEBUG] Tenant invoice created by {request.user.email}, ID={invoice.id}, audit_log_id={audit_id}")

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_update(self, serializer):
        invoice = serializer.save()
        log_invoice_action(invoice, action="tenant_invoice_updated", performed_by=self.request.user)
        print(f"[DEBUG] Tenant invoice updated by {self.request.user.email}, ID={invoice.id}")

    def perform_destroy(self, instance):
        log_invoice_action(instance, action="tenant_invoice_deleted", performed_by=self.request.user)
        print(f"[DEBUG] Tenant invoice deleted by {self.request.user.email}, ID={instance.id}")
        instance.delete()



class TenantPaymentViewSet(BaseTenantViewSet):
    queryset = TenantPayment.objects.all()
    serializer_class = TenantPaymentSerializer


class TenantViewSet(BaseTenantViewSet):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer

    def get_queryset(self):
        tenant_ids = TenantUser.objects.filter(user=self.request.user).values_list("tenant_id", flat=True)
        return Tenant.objects.filter(id__in=tenant_ids)

    def perform_create(self, serializer):
        tenant = serializer.save()
        TenantUser.objects.create(tenant=tenant, user=self.request.user, role="owner")


class TenantUserViewSet(BaseTenantViewSet):
    queryset = TenantUser.objects.all()
    serializer_class = TenantUserSerializer
    permission_classes = [RoleBasedPermission]

    def get_queryset(self):
        tenant_ids = TenantUser.objects.filter(user=self.request.user).values_list("tenant_id", flat=True)
        return TenantUser.objects.filter(tenant_id__in=tenant_ids)

    def perform_create(self, serializer):
        tenant_id = self.request.data.get("tenant_id")
        user_id = self.request.data.get("user_id")
        role = self.request.data.get("role", "member")

        tenant = Tenant.objects.get(id=tenant_id)
        user = User.objects.get(id=user_id)

        serializer.save(tenant=tenant, user=user, role=role)






class PlatformInvoiceViewSet(BaseInvoiceViewSet):
    queryset = PlatformInvoice.objects.all()
    serializer_class = PlatformInvoiceSerializer
    permission_classes = [RequirePrivilegePermission]
    basename = "platform"

    # ✅ Map each action to its required privilege
    action_privileges = {
        "list": "invoice:view",
        "retrieve": "invoice:view",
        "create": "invoice:create",
        "update": "invoice:update",
        "partial_update": "invoice:update",
        "destroy": "invoice:delete",
        # Custom actions
        "mark_paid": "invoice:update",        # privilege for marking paid
        "mark_overdue": "invoice:update",     # privilege for marking overdue
        "mark_refunded": "invoice:update",    # privilege for marking refunded
        "download_pdf": "invoice:download_pdf",
        "send_reminder": "invoice:send_reminder",
    }

    def get_required_privilege(self):
        return self.action_privileges.get(self.action)

    
    def get_permissions(self):
    # ✅ Ensure action is resolved
        action = getattr(self, "action", None)

    # ✅ Determine required privilege for this action
        required = self.get_required_privilege() if action else None

    # ✅ Explicitly set it on the view so permission class can see it
        setattr(self, "required_privilege", required)

    # ✅ Debug logging
        print(f"[DEBUG] Setting required_privilege='{required}' for action='{action}'")

    # ✅ Return the permission class
        return [RequirePrivilegePermission()]




    def get_queryset(self):
        # Only allow platform users to see invoices
        if PlatformUser.objects.filter(user=self.request.user).exists():
            return PlatformInvoice.objects.all()
        return PlatformInvoice.objects.none()

    def create(self, request, *args, **kwargs):
        self.required_privilege = self.get_required_privilege()
        self.check_permissions(request)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # ✅ Ensure tenant is attached
        tenant_id = request.data.get("tenant")
        if not tenant_id:
            return Response({"error": "tenant is required"}, status=status.HTTP_400_BAD_REQUEST)
        tenant = Tenant.objects.get(id=tenant_id)

        invoice = serializer.save(
            tenant=tenant,
            issued_at=timezone.now(),
            status=request.data.get("status", "unpaid"),
            description=request.data.get("description", "Platform invoice generated"),
        )

        # --- PDF Invoice Generation ---
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, 800, f"Platform Invoice #{invoice.id}")
        p.setFont("Helvetica", 12)
        p.drawString(50, 780, f"Amount: {invoice.amount} {invoice.currency}")
        p.drawString(50, 760, f"Due Date: {invoice.due_date}")
        p.drawString(50, 740, f"Status: {invoice.status}")
        p.showPage()
        p.save()

        buffer.seek(0)
        invoice.pdf_file.save(f"platform_invoice_{invoice.id}.pdf", buffer, save=True)

        log_invoice_action(invoice, action="platform_invoice_created", performed_by=request.user)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_update(self, serializer):
        self.required_privilege = self.get_required_privilege()
        self.check_permissions(self.request)
        invoice = serializer.save()
        log_invoice_action(invoice, action="platform_invoice_updated", performed_by=self.request.user)

    def perform_destroy(self, instance):
        self.required_privilege = self.get_required_privilege()
        self.check_permissions(self.request)
        log_invoice_action(instance, action="platform_invoice_deleted", performed_by=self.request.user)
        instance.delete()

    # ✅ Example custom action: mark_paid
    @action(detail=True, methods=["patch"])
    def mark_paid(self, request, pk=None):
        self.required_privilege = self.get_required_privilege()
        self.check_permissions(request)

        invoice = self.get_object()
        invoice.status = "paid"
        invoice.save()

        log_invoice_action(invoice, action="platform_invoice_marked_paid", performed_by=request.user)
        return Response({"status": "paid"}, status=status.HTTP_200_OK)
