from django.conf import settings
from saas_app.core.models import Payment, TenantUser, PlatformUser
from django.core.mail import EmailMessage
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO

# ------------------
# Feature check
# ------------------
def has_feature(tier, feature_name: str) -> bool:
    """
    Return True if the given tier has the specified feature.
    Assumes tier.features is a list of strings.
    """
    if not tier:
        return False
    features = tier.features or []
    return feature_name in features

# ------------------
# Payment creation
# ------------------
def create_payment(tenant, tier, amount, reference, provider):
    return Payment.objects.create(
        tenant=tenant,
        tier=tier,
        amount=amount,
        reference=reference,
        provider=provider,
        status="pending"
    )

# ------------------
# Auto send invoice
# ------------------
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

# ------------------
# Role detection
# ------------------
def get_user_role(user):
    """
    Determine the role of a user based on related models.
    """
    # Check tenant roles
    tenant_user = TenantUser.objects.filter(user=user).first()
    if tenant_user:
        return tenant_user.role

    # Check platform roles
    platform_user = getattr(user, "platformuser", None)
    if platform_user:
        return platform_user.role

    # Fallbacks
    if user.is_superuser:
        return "platform_owner"
    elif user.is_staff:
        return "staff"
    return "tenant_user"
