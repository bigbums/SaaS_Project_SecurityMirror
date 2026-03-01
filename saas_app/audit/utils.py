from saas_app.audit.models import AuditTrail

def log_invoice_action(invoice, action, performed_by=None, transaction_id=None):
    AuditTrail.objects.create(
        tenant=invoice.tenant,
        user=performed_by,
        action=action,
        object_id=invoice.id,
        object_type=invoice.__class__.__name__,
        details={"transaction_id": transaction_id} if transaction_id else {}
    )
