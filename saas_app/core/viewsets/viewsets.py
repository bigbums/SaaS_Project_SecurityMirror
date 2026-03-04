from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from django.contrib.auth import get_user_model
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import io
import uuid

from saas_app.core.permissions import (
    IsTenantOwner,
    RoleBasedPermission,
    RequirePrivilegePermission,
    TenantRequirePrivilegePermission,
)
from saas_app.core.viewsets.base import BaseTenantViewSet
from saas_app.core.viewsets.base_invoice_viewset import BaseInvoiceViewSet
from saas_app.core.models import (
    Sale, SaleItem, Item, TenantCustomer, TenantInvoice, Tier,
    Location, Payment, PlatformInvoice, TenantPayment,
    Tenant, TenantUser, User, PlatformUser,
)
from saas_app.core.serializers import (
    SaleSerializer, SaleItemSerializer, UserSerializer,
    ItemSerializer, TenantCustomerSerializer, TenantInvoiceSerializer,
    TenantPaymentSerializer, TenantSerializer, TenantUserSerializer,
    PlatformInvoiceSerializer,
)
from saas_app.core.constants import INVOICE_STATUS_CHOICES
from saas_app.core.invoice_actions import (
    MarkPaidSerializer,
    MarkRefundedSerializer,
    DownloadPDFSerializer,
    SendReminderSerializer,
)
from saas_app.core.utils.logging_helpers import log_invoice_action   # ✅ only this one

__all__ = [
    "UserViewSet",
    "ItemViewSet",
    "SaleViewSet",
    "SaleItemViewSet",
    "TenantCustomerViewSet",
    "TenantInvoiceViewSet",
    "TenantPaymentViewSet",
    "TenantViewSet",
    "TenantUserViewSet",
    "PlatformInvoiceViewSet",
]
