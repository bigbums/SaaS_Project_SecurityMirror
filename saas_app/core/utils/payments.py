import requests
from django.conf import settings
from django.utils import timezone
from saas_app.core.utils.logging_helpers import log_invoice_action


PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY
PAYSTACK_BASE_URL = "https://api.paystack.co"


# -------------------------------
# Online Payment Initialization
# -------------------------------

def create_payment(user, invoice, amount, email=None, currency="NGN"):
    """
    Initialize a Paystack transaction and save a Payment record.
    Also stores the Paystack reference in the invoice for webhook matching.
    """
    if email is None:
        email = user.email

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "email": email,
        "amount": int(amount * 100),  # Paystack expects kobo
        "currency": currency,
        "metadata": {
            "user_id": user.id,
            "username": user.username,
            "invoice_id": invoice.id,  # helpful for debugging
        },
    }

    response = requests.post(f"{PAYSTACK_BASE_URL}/transaction/initialize", json=data, headers=headers)
    res_data = response.json()

    if res_data.get("status"):
        reference = res_data["data"]["reference"]

        # Store reference in invoice for webhook lookup
        invoice.audit_log_id = reference
        invoice.save(update_fields=["audit_log_id"])

        from saas_app.core.models import Payment
        payment = Payment.objects.create(
            user=user,
            amount=amount,
            currency=currency,
            status="pending",
            provider="paystack",
            provider_id=reference,
        )
        return res_data["data"]["authorization_url"], payment
    else:
        raise Exception(f"Paystack error: {res_data}")


# -------------------------------
# Unified Payment Recorder
# -------------------------------
def record_payment(invoice, amount, method, transaction_id=None, receipt_number=None, proof_file=None):
    """
    Generic payment recorder for both TenantInvoice and PlatformInvoice.
    Creates a Payment record, marks invoice as paid, and logs the action.
    """
    # Generate defaults if not provided
    if not transaction_id:
        transaction_id = f"{method.upper()}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
    if not receipt_number:
        receipt_number = transaction_id

    payment = invoice.payments.create(
        amount=amount,
        method=method,
        transaction_id=transaction_id,
        receipt_number=receipt_number,
        proof_file=proof_file,
    )

    # Mark invoice as paid
    invoice.mark_paid(transaction_id=payment.transaction_id)

    # Log action
    log_invoice_action(invoice, action=f"{method}_payment_recorded", transaction_id=payment.transaction_id)

    return payment


# -------------------------------
# Wrappers for Specific Methods
# -------------------------------
def record_cash_payment(invoice, amount, receipt_number=None):
    transaction_id = receipt_number or f"CASH-{timezone.now().strftime('%Y%m%d%H%M%S')}"
    return record_payment(
        invoice=invoice,
        amount=amount,
        method="cash",
        transaction_id=transaction_id,
        receipt_number=transaction_id,
    )


def record_teller_payment(invoice, amount, teller_number, proof_file=None):
    return record_payment(
        invoice=invoice,
        amount=amount,
        method="bank_teller",
        transaction_id=teller_number,
        receipt_number=f"TELLER-{teller_number}",
        proof_file=proof_file,
    )


def record_bank_transfer(invoice, amount, bank_ref, proof_file=None):
    return record_payment(
        invoice=invoice,
        amount=amount,
        method="bank_transfer",
        transaction_id=bank_ref,
        receipt_number=f"TRANSFER-{bank_ref}",
        proof_file=proof_file,
    )


#Verify Payments

def verify_payment(reference):
    """
    Verify a Paystack payment using the transaction reference.
    Returns the JSON response from Paystack.
    """
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    response = requests.get(f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}", headers=headers)
    return response.json()
