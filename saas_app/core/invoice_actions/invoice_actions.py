# saas_app/core/serializers/invoice_actions.py

from rest_framework import serializers
from saas_app.core.models import TenantInvoice, PlatformInvoice
from saas_app.core.constants import PAYMENT_METHOD_CHOICES, INVOICE_STATUS_CHOICES
from django.utils import timezone

class MarkPaidSerializer(serializers.ModelSerializer):
    payment_method = serializers.ChoiceField(choices=[c[0] for c in PAYMENT_METHOD_CHOICES])
    payment_reference = serializers.CharField(required=False, allow_blank=True)
    confirmed_by = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = TenantInvoice  # or PlatformInvoice depending on context
        fields = ["id", "status", "payment_method", "payment_reference", "confirmed_by"]

    def validate(self, data):
        if self.instance.status == "paid":
            raise serializers.ValidationError("Invoice is already marked as paid.")
        return data

    def save(self, **kwargs):
        payment_method = self.validated_data.get("payment_method")
        if payment_method in ["bank_lodgement", "bank_transfer"]:
            self.instance.status = "pending_confirmation"
        else:
            self.instance.status = "paid"
        self.instance.payment_method = payment_method
        self.instance.payment_reference = self.validated_data.get("payment_reference")
        self.instance.confirmed_by = self.validated_data.get("confirmed_by")
        self.instance.save()
        return self.instance


class MarkRefundedSerializer(serializers.ModelSerializer):
    """
    Serializer for marking invoices as refunded.
    Ensures only 'paid' invoices can be refunded.
    """
    class Meta:
        model = TenantInvoice  # or PlatformInvoice depending on context
        fields = ["id", "status"]

    def validate(self, data):
        if self.instance.status != "paid":
            raise serializers.ValidationError(
                f"Only invoices with status 'paid' can be refunded. Current status: {self.instance.status}"
            )
        return data

    def save(self, **kwargs):
        valid_statuses = [c[0] for c in INVOICE_STATUS_CHOICES]
        if "refunded" not in valid_statuses:
            raise serializers.ValidationError("'refunded' is not a valid status.")
        self.instance.status = "refunded"
        self.instance.refunded_at = timezone.now()
        self.instance.save()
        return self.instance


class DownloadPDFSerializer(serializers.Serializer):
    invoice_id = serializers.IntegerField()


class SendReminderSerializer(serializers.Serializer):
    invoice_id = serializers.IntegerField()
    recipient_email = serializers.EmailField()
