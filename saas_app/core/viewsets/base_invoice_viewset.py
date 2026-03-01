# core/viewsets/base_invoice_viewset.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

# ✅ Invoice action serializers (specialized package)
from saas_app.core.invoice_actions import (
    MarkPaidSerializer,
    MarkRefundedSerializer,
)

from saas_app.core.utils.logging_helpers import log_invoice_action
from saas_app.core.constants import INVOICE_STATUS_CHOICES



class BaseInvoiceViewSet(viewsets.ModelViewSet):
    """
    Shared base class for TenantInvoiceViewSet and PlatformInvoiceViewSet.
    Provides consistent mark_paid, mark_overdue, and mark_refunded logic.
    """

    basename = None  # must be set in child classes

    @action(detail=True, methods=["patch"])
    def mark_paid(self, request, pk=None):
        self.required_privilege = self.get_required_privilege()
        self.check_permissions(request)
        invoice = self.get_object()

        serializer = MarkPaidSerializer(invoice, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        valid_statuses = [choice[0] for choice in INVOICE_STATUS_CHOICES]
        if invoice.status not in valid_statuses:
            return Response(
                {"error": f"Invalid status '{invoice.status}'. Must be one of {valid_statuses}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        log_invoice_action(
            invoice,
            action=f"{self.basename}_invoice_marked_paid",
            performed_by=request.user,
            transaction_id=serializer.validated_data.get("payment_reference")
        )
        return Response({"success": True, "status": invoice.status})

    @action(detail=True, methods=["patch"])
    def mark_overdue(self, request, pk=None):
        self.required_privilege = self.get_required_privilege()
        self.check_permissions(request)
        invoice = self.get_object()

        valid_statuses = [choice[0] for choice in INVOICE_STATUS_CHOICES]
        if invoice.status not in valid_statuses:
            return Response(
                {"error": f"Invalid status '{invoice.status}'. Must be one of {valid_statuses}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if invoice.due_date < timezone.now().date() and invoice.status == "pending":
            invoice.status = "overdue"
            invoice.save()
            log_invoice_action(
                invoice,
                action=f"{self.basename}_invoice_marked_overdue",
                performed_by=request.user
            )

        return Response({"success": True, "status": invoice.status})

   
    @action(detail=True, methods=["patch"])
    def mark_refunded(self, request, pk=None):
        """
        Marks an invoice as refunded if its current status is 'paid'.
        Uses MarkRefundedSerializer for validation.
        """
        self.required_privilege = self.get_required_privilege()
        self.check_permissions(request)
        invoice = self.get_object()

        serializer = MarkRefundedSerializer(invoice, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        log_invoice_action(
            invoice,
            action=f"{self.basename}_invoice_marked_refunded",
            performed_by=request.user
        )

        return Response({"success": True, "status": invoice.status})
