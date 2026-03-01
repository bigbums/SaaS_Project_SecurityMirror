# saas_app/core/constants.py

PLAN_FEATURES = {
    "free": {
        "branding": False,
        "analytics_basic": False,
        "analytics_advanced": False,
        "support": "community",
        "storage_limit_mb": 100,
        "multi_tenant": False,
        "integrations": 0,
        "invoice_customization": False,
        "user_limit": 1,
    },
    "basic": {
        "branding": "logo_only",
        "analytics_basic": True,
        "analytics_advanced": False,
        "support": "email",
        "storage_limit_mb": 1000,
        "multi_tenant": False,
        "integrations": 1,
        "invoice_customization": "limited",
        "user_limit": 3,
    },
    "pro": {
        "branding": True,
        "analytics_basic": True,
        "analytics_advanced": True,
        "support": "priority",
        "storage_limit_mb": 10000,
        "multi_tenant": True,
        "integrations": 5,
        "invoice_customization": True,
        "user_limit": 10,
    },
    "enterprise": {
        "branding": "white_label",
        "analytics_basic": True,
        "analytics_advanced": True,
        "support": "dedicated_manager",
        "storage_limit_mb": None,  # unlimited
        "multi_tenant": True,
        "integrations": None,      # unlimited
        "invoice_customization": "white_label",
        "user_limit": None,        # unlimited
    },
}

# ✅ Unified payment method choices for invoices
# saas_app/core/constants.py

INVOICE_STATUS_CHOICES = [
    ("unpaid", "Unpaid"),
    ("pending", "Pending"),
    ("pending_confirmation", "Pending Confirmation"),
    ("paid", "Paid"),
    ("overdue", "Overdue"),
    ("refunded", "Refunded"),  # <-- new status added
]

PAYMENT_METHOD_CHOICES = [
    ("cash", "Cash"),
    ("bank_lodgement", "Bank Lodgement"),
    ("bank_transfer", "Bank Transfer"),
    ("paystack", "Paystack"),
    ("opay", "Opay"),
    # add more gateways here if needed
]

# core/constants.py
# ISO 4217 currency codes (extend or load dynamically)
VALID_CURRENCIES = {
    "USD",  # US Dollar
    "EUR",  # Euro
    "GBP",  # British Pound
    "NGN",  # Nigerian Naira
    "CAD",  # Canadian Dollar
    "JPY",  # Japanese Yen
    "AUD",  # Australian Dollar
    "CHF",  # Swiss Franc
    "GHS",  # Ghanaian Cedi
    "XOF",  # West African CFA franc (Benin, WAEMU)
}
