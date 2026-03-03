from django.core.mail import EmailMessage
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO

def send_invoice_email(payment):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, "Invoice / Receipt")
    p.setFont("Helvetica", 12)
    p.drawString(100, 780, f"Invoice Number: {payment.invoice_number}")
    p.drawString(100, 760, f"Tenant: {payment.tenant.name}")
    p.drawString(100, 740, f"Tier: {payment.tier.name}")
    p.drawString(100, 720, f"Amount: ₦{payment.amount // 100}")
    p.drawString(100, 700, f"Provider: {payment.provider.title()}")
    p.drawString(100, 680, f"Reference: {payment.reference}")
    p.drawString(100, 660, f"Date: {payment.created_at.strftime('%Y-%m-%d %H:%M')}")
    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()

    subject = f"Invoice {payment.invoice_number} - {payment.tier.name} Plan"
    body = f"Dear {payment.tenant.name},\n\nAttached is your invoice for the {payment.tier.name} plan.\n\nThank you for your payment!"
    email = EmailMessage(subject, body, to=[payment.tenant.email])
    email.attach(f"invoice_{payment.invoice_number}.pdf", pdf, "application/pdf")
    email.send()
