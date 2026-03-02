from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from saas_app.core.constants import PAYMENT_METHOD_CHOICES, INVOICE_STATUS_CHOICES

from saas_app.core.utils.logging_helpers import log_invoice_action






User = get_user_model()



# ---------------------
# PlatformUser Model
# ---------------------

class PlatformUser(models.Model):
    ROLE_CHOICES = [
        ("platform_owner", "Platform Owner"),
        ("platform_admin", "Platform Admin"),
        ("platform_manager", "Platform Manager"),
        ("platform_user", "Platform User"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="platform_profile"
    )
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default="platform_user")
    last_login = models.DateTimeField(null=True, blank=True)
    last_logout = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} ({self.role})"

    def save(self, *args, **kwargs):
        # Enforce that only Platform Owners can manage platform users
        request = kwargs.pop("request", None)
        if request:
            platform_user = PlatformUser.objects.filter(user=request.user).first()
            if not platform_user or platform_user.role != "platform_owner":
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Only Platform Owners can manage platform users.")
        super().save(*args, **kwargs)



# -----------------------------
# Tier Model
# -----------------------------
class Tier(models.Model):
    name = models.CharField(max_length=50, unique=True)
    max_users = models.IntegerField(null=True, blank=True)
    max_locations = models.IntegerField(null=True, blank=True)
    price = models.IntegerField(default=0)  # NGN
    features = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.name


# -----------------------------
# Tenant Model
# -----------------------------
class Tenant(models.Model):
    name = models.CharField(max_length=255, unique=True, default="Untitled Tenant")
    email = models.EmailField(blank=True, null=True)
    tier = models.ForeignKey("core.Tier", on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default="active")
    created_at = models.DateTimeField(auto_now_add=True)

    current_users_count = models.IntegerField(default=0)
    current_locations_count = models.IntegerField(default=0)

    def natural_key(self):
        return (self.name,)
        natural_key.dependencies = ['core.PlatformCustomer'] # ensures invoices can resolve tenant

    def can_add_user(self):
        return (self.tier.max_users is None) or (self.current_users_count < self.tier.max_users)

    def can_add_location(self):
        return (self.tier.max_locations is None) or (self.current_locations_count < self.tier.max_locations)

    def __str__(self):
        return f"{self.name} ({self.tier.name})"


# -----------------------------
# TenantUser Model
# -----------------------------

class TenantUser(models.Model):
    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("manager", "Manager"),
        ("member", "Member"),
    ]

    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE, related_name="users")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tenants")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="member")
    last_login = models.DateTimeField(null=True, blank=True)
    last_logout = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return f"{self.user.email} ({self.role}) in {self.tenant.name}"

    def save(self, *args, **kwargs):
        # Enforce that only owners can manage tenant users
        request = kwargs.pop("request", None)
        if request:
            tenant_user = TenantUser.objects.filter(user=request.user, tenant=self.tenant).first()
            if not tenant_user or tenant_user.role != "owner":
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Only owners can manage tenant users.")
        super().save(*args, **kwargs)



# -----------------------------
# Project Model
# -----------------------------
class Project(models.Model):
    name = models.CharField(max_length=200, default="New Project")
    status = models.CharField(max_length=50, default="active")
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


# -----------------------------
# Item Model
# -----------------------------
class Item(models.Model):
    ITEM_TYPE_CHOICES = [
        ("product", "Product"),
        ("service", "Service"),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, default="Untitled")
    type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES, default="product")
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.type})"


class Sale(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    invoice_number = models.CharField(max_length=50, unique=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            year = timezone.now().year
            last_sale = Sale.objects.filter(created_at__year=year).order_by("id").last()
            last_seq = 0
            if last_sale and last_sale.invoice_number:
                try:
                    last_seq = int(last_sale.invoice_number.split("-")[-1])
                except:
                    last_seq = 0
            new_seq = last_seq + 1
            self.invoice_number = f"INV-{year}-{new_seq:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.total_amount}"


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name="items", on_delete=models.CASCADE)
    item = models.ForeignKey(Item, null=True, blank=True, on_delete=models.SET_NULL)
    quantity = models.PositiveIntegerField(default=1)
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        if self.item and self.item.type == "product":
            if self.item.stock >= self.quantity:
                self.item.stock -= self.quantity
                self.item.save()
            else:
                raise ValueError("Insufficient stock for product")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item.name} x {self.quantity}" if self.item else "Unknown Item"

# -----------------------------
# Location Model
# -----------------------------
class Location(models.Model):
    tenant = models.ForeignKey(Tenant, related_name="locations", on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.tenant.name})"


#-------------------
# Payment Model
#-------------------

class Payment(models.Model):
    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE, related_name="payments")
    tier = models.ForeignKey("core.Tier", on_delete=models.SET_NULL, null=True)
    amount = models.IntegerField()  # stored in kobo
    reference = models.CharField(max_length=100, unique=True)
    invoice_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    status = models.CharField(max_length=20, default="pending")  # pending, success, failed
    provider = models.CharField(max_length=20)  # paystack or opay
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Generate sequential invoice number: INV-YYYY-XXX
            year = self.created_at.year if self.created_at else 2026
            last_invoice = Payment.objects.filter(invoice_number__startswith=f"INV-{year}").order_by("-id").first()
            if last_invoice and last_invoice.invoice_number:
                last_seq = int(last_invoice.invoice_number.split("-")[-1])
            else:
                last_seq = 0
            self.invoice_number = f"INV-{year}-{last_seq+1:03d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_number} - {self.tenant.name} - {self.status}"

#---------------------------------
# Tenant Invoice Model - Old Model
#---------------------------------
"""
class TenantInvoice(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("overdue", "Overdue"),
        ("cancelled", "Cancelled"),
    ]

    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE)
    customer = models.ForeignKey("TenantCustomer", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="NGN")

    due_date = models.DateField(default=timezone.now)
    issued_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    pdf_file = models.FileField(upload_to="tenant_invoices/", null=True, blank=True)

    # Compliance field
    audit_log_id = models.CharField(max_length=64, blank=True, help_text="Reference ID for audit trail")

    class Meta:
        ordering = ["-issued_at"]
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["due_date"]),
        ]
        permissions = [
            ("can_generate_tenant_invoice", "Can generate tenant invoices"),
            ("can_manage_tenant_invoice", "Can edit/delete tenant invoices"),
            ("can_view_tenant_invoice", "Can view tenant invoices"),
        ]

    def __str__(self):
        return f"TenantInvoice {self.id} - {self.customer.name} ({self.status})"

def mark_paid(self, transaction_id=None):
    self.status = "paid"
    self.paid_at = timezone.now()
    self.save()
    from core.utils.logging_helpers import log_invoice_action
    log_invoice_action(self, action="tenant_invoice_paid", performed_by=None, transaction_id=transaction_id)

def mark_overdue(self):
    if self.due_date < timezone.now().date() and self.status == "pending":
        self.status = "overdue"
        self.save()
        from core.utils.logging_helpers import log_invoice_action
        log_invoice_action(self, action="tenant_invoice_overdue")
"""

#--------------------------------------
# Tenant Invoice Model (Hybrid Design) - With denormalized snapshot
#--------------------------------------

class TenantInvoice(models.Model):
  
    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE)
    tenant_name = models.CharField(max_length=255, blank=True)  # snapshot of tenant name
    customer = models.ForeignKey("TenantCustomer", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)


    due_date = models.DateField(default=timezone.now)
    issued_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=32, choices=INVOICE_STATUS_CHOICES, default="pending")
    description = models.TextField(default="Invoice generated")
    pdf_file = models.FileField(upload_to="tenant_invoices/", blank=True, null=True)

    audit_log_id = models.CharField(max_length=64, blank=True, help_text="Reference ID for audit trail")

    # Unified payment tracking fields
    payment_method = models.CharField(max_length=32, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    payment_reference = models.CharField(max_length=128, null=True, blank=True)
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="confirmed_tenant_invoices"
    )
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-issued_at"]
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["due_date"]),
        ]
        permissions = [
            ("can_generate_tenant_invoice", "Can generate tenant invoices"),
            ("can_manage_tenant_invoice", "Can edit/delete tenant invoices"),
            ("can_view_tenant_invoice", "Can view tenant invoices"),
        ]

    def save(self, *args, **kwargs):
        if self.tenant and not self.tenant_name:
            self.tenant_name = self.tenant.name
        super().save(*args, **kwargs)

    def __str__(self):
        return f"TenantInvoice {self.id} - {self.tenant_name} / {self.customer.name} ({self.status})"

 



    def mark_paid(self, transaction_id=None, user=None):
        self.status = "paid"
        self.paid_at = timezone.now()
        self.confirmed_by = user
        self.confirmed_at = timezone.now()
        self.save()

        # Updated logger call
        log_invoice_action(
            self,
            action="tenant_invoice_paid",
            performed_by=user,
            transaction_id=transaction_id
        )

    def mark_overdue(self):
        if self.due_date < timezone.now().date() and self.status == "pending":
            self.status = "overdue"
            self.save()

            # Updated logger call
            log_invoice_action(
                self,
                action="tenant_invoice_overdue"
            )


# ----Currency Model----
# core/models.py
class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)  # ISO 4217 code
    name = models.CharField(max_length=64)              # e.g., "Ghanaian Cedi"
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["code"]
        app_label = "core"

    def __str__(self):
        return f"{self.code} - {self.name}"



#---------------------------------
# Billing - Platform Invoice Model
#---------------------------------


class PlatformInvoice(models.Model):
   
   
    tenant = models.ForeignKey("Tenant", on_delete=models.CASCADE)
    customer = models.ForeignKey("PlatformCustomer", on_delete=models.CASCADE, null=False, blank=False, default=1)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)


    due_date = models.DateField()
    issued_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=32, choices=INVOICE_STATUS_CHOICES, default="pending")
    description = models.TextField(default="Platform invoice generated")
    pdf_file = models.FileField(upload_to="platform_invoices/", null=True, blank=True)

    # Compliance field
    audit_log_id = models.CharField(max_length=64, blank=True, help_text="Reference ID for audit trail")

    # Snapshot of platform company name
    platform_name = models.CharField(max_length=255, blank=True)

    # New payment tracking fields
    payment_method = models.CharField(max_length=32, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    payment_reference = models.CharField(max_length=128, null=True, blank=True)  # teller number, transfer ref, gateway txn ID
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="confirmed_platform_invoices"
    )
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-issued_at"]
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["due_date"]),
        ]
        permissions = [
            ("can_generate_platform_invoice", "Can generate platform invoices"),
            ("can_manage_platform_invoice", "Can edit/delete platform invoices"),
            ("can_view_platform_invoice", "Can view platform invoices"),
        ]

    def save(self, *args, **kwargs):
        if not self.platform_name:
            self.platform_name = settings.PLATFORM_COMPANY_NAME
        super().save(*args, **kwargs)

    def __str__(self):
        return f"PlatformInvoice {self.id} - {self.platform_name} ({self.status})"





    def mark_paid(self, transaction_id=None, user=None):
        self.status = "paid"
        self.paid_at = timezone.now()
        self.confirmed_by = user
        self.confirmed_at = timezone.now()
        self.save()

        # Updated logger call
        log_invoice_action(
            self,
            action="platform_invoice_paid",
            performed_by=user,
            transaction_id=transaction_id
        )

    def mark_overdue(self):
        if self.due_date < timezone.now().date() and self.status == "pending":
            self.status = "overdue"
            self.save()

            # Updated logger call
            log_invoice_action(
                self,
                action="platform_invoice_overdue"
            )

"""
 PAYMENT_METHOD_CHOICES = [
        ("cash", "Cash"),
        ("bank_teller", "Bank Teller"),
        ("bank_transfer", "Bank Transfer"),
        ("paystack", "Paystack"),
        ("opay", "Opay"),
    ]
        """

class PlatformPayment(models.Model):
    invoice = models.ForeignKey(PlatformInvoice, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)

    # For digital payments: gateway transaction ID
    # For bank transfers: bank reference number
    # For cash/teller: generated receipt number
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)

    # Internal receipt number for consistency across all methods
    receipt_number = models.CharField(max_length=50, unique=True, null=True, blank=True)

    # Optional proof upload (e.g. scanned teller slip, transfer screenshot)
    proof_file = models.FileField(upload_to="platform_payments/", null=True, blank=True)

    paid_at = models.DateTimeField(auto_now_add=True)


#-----------------------
# Billing - Tenant Invoice Model
#-----------------------

class TenantCustomer(models.Model):
    tenant = models.ForeignKey("Tenant", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()

    


    def __str__(self):
        return f"{self.name} ({self.email})"


class PlatformCustomer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.name} ({self.email})"



METHOD_CHOICES = [
    ("cash", "Cash"),
    ("bank_teller", "Bank Teller"),
    ("bank_transfer", "Bank Transfer"),
    ("paystack", "Paystack"),
    ("opay", "Opay"),
]

class TenantPayment(models.Model):
    invoice = models.ForeignKey(TenantInvoice, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=50, choices=METHOD_CHOICES)

    # For digital payments, this is the gateway transaction ID.
    # For bank transfers, this can be the bank reference number.
    # For cash/teller, this can be a generated receipt number.
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)

    # System-generated receipt number for internal tracking
    receipt_number = models.CharField(max_length=50, unique=True, null=True, blank=True)

    # Optional proof upload (e.g. scanned teller slip, transfer screenshot)
    proof_file = models.FileField(upload_to="tenant_payments/", null=True, blank=True)

    paid_at = models.DateTimeField(auto_now_add=True)

#-----Storage Type Config----

class PlatformTenantConfig(models.Model):
    tenant = models.OneToOneField("core.Tenant", on_delete=models.CASCADE, related_name="platform_config")
    storage_type = models.CharField(max_length=50, choices=[("cloud", "Cloud"), ("local", "Local")], default="cloud")
    hosting_type = models.CharField(max_length=20, choices=[("cloud", "Cloud"), ("onprem", "On‑Premise")], default="cloud")
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.tenant.name} ({self.hosting_type}, {self.storage_type})"




