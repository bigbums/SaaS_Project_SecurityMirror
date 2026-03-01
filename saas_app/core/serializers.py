from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from .models import (
    Sale, SaleItem, Item, Location, TenantCustomer, Payment, Tier,
    TenantInvoice, TenantPayment, Tenant, TenantUser, Tier, PlatformInvoice
)
from saas_app.core.models import TenantUser, Tenant, TenantInvoice, PlatformInvoice
#from .serializers import UserSerializer, TenantSerializer  # adjust if needed
from django.utils import timezone
from saas_app.core.validators import validate_currency
from django.utils import timezone
from .constants import VALID_CURRENCIES   # ✅ make sure this is defined in constants.py

from saas_app.core.invoice_actions.base_invoice import BaseInvoiceSerializer



User = get_user_model()


class SaleItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="item.name", read_only=True)
    item_type = serializers.CharField(source="item.type", read_only=True)

    class Meta:
        model = SaleItem
        fields = ["id", "sale", "item", "item_name", "item_type", "quantity", "line_total"]


class SaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = ["id", "date", "total_amount", "status"]



class TenantInvoiceSerializer(BaseInvoiceSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)

    tenant = serializers.PrimaryKeyRelatedField(
        queryset=TenantInvoice._meta.get_field("tenant").related_model.objects.all(),
        required=True,
        error_messages={"required": "Tenant is required"}
    )
    customer = serializers.PrimaryKeyRelatedField(
        queryset=TenantInvoice._meta.get_field("customer").related_model.objects.all(),
        required=True,
        error_messages={"required": "Customer is required"}
    )

    class Meta:
        model = TenantInvoice
        fields = [
            "id", "tenant", "customer", "customer_name",
            "amount", "currency", "due_date", "issued_at",
            "paid_at", "status", "description", "audit_log_id"
        ]
        read_only_fields = ["issued_at", "paid_at"]





class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ["id", "name", "type", "description", "price", "stock"]


class TenantCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantCustomer
        fields = ["id", "tenant", "name", "email"]
        read_only_fields = ["tenant"]



class PlatformInvoiceSerializer(BaseInvoiceSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)

    tenant = serializers.PrimaryKeyRelatedField(
        queryset=PlatformInvoice._meta.get_field("tenant").related_model.objects.all(),
        required=True,
        error_messages={"required": "Tenant is required"}
    )
    customer = serializers.PrimaryKeyRelatedField(
        queryset=PlatformInvoice._meta.get_field("customer").related_model.objects.all(),
        required=True,
        error_messages={"required": "Customer is required"}
    )

    class Meta:
        model = PlatformInvoice
        fields = [
            "id", "tenant", "customer", "customer_name",
            "amount", "currency", "due_date", "issued_at",
            "paid_at", "status", "description", "audit_log_id"
        ]
        read_only_fields = ["issued_at", "paid_at"]







class TenantPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantPayment
        fields = ["id", "invoice", "amount", "method", "transaction_id", "paid_at"]
        read_only_fields = ["paid_at"]


class TierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tier
        fields = ["id", "name", "max_users", "max_locations", "price", "features"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email"]


class TenantSerializer(serializers.ModelSerializer):
    tier_id = serializers.PrimaryKeyRelatedField(
        queryset=Tier.objects.all(),
        source="tier",
        write_only=True
    )
    tier = TierSerializer(read_only=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = Tenant
        fields = ["id", "name", "email", "tier", "tier_id"]




class TenantUserSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="user",
        write_only=True
    )
    tenant_id = serializers.PrimaryKeyRelatedField(
        queryset=Tenant.objects.all(),
        source="tenant",
        write_only=True
    )

    user = UserSerializer(read_only=True)
    tenant = TenantSerializer(read_only=True)

    class Meta:
        model = TenantUser
        fields = ["id", "tenant", "tenant_id", "user", "user_id", "role"]

    def validate(self, data):
        request = self.context.get("request")
        tenant = data.get("tenant") or getattr(self.instance, "tenant", None)

        is_owner = TenantUser.objects.filter(
            tenant=tenant,
            user=request.user,
            role="owner"
        ).exists()

        if not is_owner:
            raise PermissionDenied("Only owners can manage tenant users.")

        return data

