# core/utils/logging_helpers.py
import json
import logging
from django.utils import timezone

def log_json(logger: logging.Logger, level: str, entry: dict, request=None):
    """
    Logs a dictionary as a JSON string with a unified schema.
    Automatically injects timestamp and correlation_id if missing.
    """
    if "timestamp" not in entry:
        entry["timestamp"] = timezone.now().isoformat()

    if "correlation_id" not in entry and request is not None:
        entry["correlation_id"] = getattr(request, "correlation_id", "none")

    message = json.dumps(entry)
    log_method = getattr(logger, level, None)
    if callable(log_method):
        log_method(message)
    else:
        logger.error(f"Invalid log level: {level}. Entry: {message}")


def log_invoice_action(invoice, action, performed_by=None, transaction_id=None, details=None):
    """
    Structured logger for invoice actions.
    Automatically captures payment fields if present on the invoice.
    Adds refunded_at when invoice is refunded.
    """
    entry = {
        "event": "invoice_action",
        "invoice_id": invoice.id,
        "tenant_id": getattr(invoice, "tenant_id", None),
        "action": action,
        "performed_by": getattr(performed_by, "username", None),
        "transaction_id": transaction_id,
        "status": invoice.status,
        "payment_method": getattr(invoice, "payment_method", None),
        "payment_reference": getattr(invoice, "payment_reference", None),
        "confirmed_by": getattr(invoice.confirmed_by, "username", None) if getattr(invoice, "confirmed_by", None) else None,
        "confirmed_at": invoice.confirmed_at.isoformat() if getattr(invoice, "confirmed_at", None) else None,
    }

    # Add refunded_at if invoice is refunded
    if invoice.status == "refunded" and hasattr(invoice, "refunded_at"):
        entry["refunded_at"] = invoice.refunded_at.isoformat() if invoice.refunded_at else None

    # Merge any extra details passed in
    if details:
        entry.update(details)

    log_json(logging.getLogger("invoice"), "info", entry)
