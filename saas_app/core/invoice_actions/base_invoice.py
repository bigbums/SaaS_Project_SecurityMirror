from rest_framework import serializers
from django.utils import timezone
from saas_app.core.constants import VALID_CURRENCIES


class BaseInvoiceSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        required=True,
        error_messages={"required": "Amount is required"}
    )
    currency = serializers.CharField(
        required=True,
        error_messages={"required": "Currency is required"}
    )
    due_date = serializers.DateField(
        required=True,
        error_messages={"required": "Due date is required"}
    )

    class Meta:
        # No model here — subclasses will define it
        fields = ["amount", "currency", "due_date"]
        abstract = True  # mark as abstract so Django knows this is not a concrete serializer

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate_due_date(self, value):
        today = timezone.now().date()
        if value < today:
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value

    def validate_currency(self, value):
        if value not in VALID_CURRENCIES:
            raise serializers.ValidationError("Invalid currency code.")
        return value
