# core/utils/emails.py
from django.core.mail import send_mail
from django.conf import settings

def send_invoice_email(user, invoice):
    """
    Sends an invoice email to the user.
    """
    subject = f"Invoice #{invoice.id}"
    message = f"Dear {user.username},\n\nHere is your invoice for {invoice.amount} {invoice.currency}.\n\nThank you."
    recipient = [user.email]

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient)
