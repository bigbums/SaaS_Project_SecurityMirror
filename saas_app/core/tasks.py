from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_invoice_email(user_email, invoice_id):
    subject = f"Invoice #{invoice_id}"
    message = f"Your invoice {invoice_id} is ready."
    send_mail(subject, message, "billing@yourapp.com", [user_email])
    return f"Invoice email sent to {user_email}"
