import logging

class CorrelationIdFilter(logging.Filter):
    """
    Attaches a correlation_id to log records if available in request context.
    For now, just adds a placeholder.
    """
    def filter(self, record):
        # If you have middleware that sets correlation_id, attach it here
        record.correlation_id = getattr(record, "correlation_id", "N/A")
        return True
