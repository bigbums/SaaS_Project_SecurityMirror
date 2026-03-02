# core/middleware/AuditLoggingMiddleware.py
import logging
from saas_app.core.utils.logging_helpers import log_json

audit_logger = logging.getLogger("audit")

class AuditLoggingMiddleware:
    """
    Middleware that logs every incoming request with correlation ID and metadata,
    but skips static files, favicon, and health-check endpoints.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Paths to skip
        skip_paths = [
            "/favicon.ico",
            "/robots.txt",
            "/health/",
            "/healthz",
            "/metrics",
        ]
        if request.path.startswith("/static/") or request.path.startswith("/media/"):
            return self.get_response(request)
        if request.path in skip_paths:
            return self.get_response(request)

        # Collect request metadata
        user_email = request.user.email if request.user.is_authenticated else "anonymous"

        log_entry = {
            "event": "audit",
            "message": "audit log entry",
            "user": user_email,
            "path": request.path,
            "method": request.method,
            "ip": request.META.get("REMOTE_ADDR"),
            "user_agent": request.META.get("HTTP_USER_AGENT", "unknown"),
        }

        # ✅ Helper will inject timestamp and correlation_id automatically
        log_json(audit_logger, "info", log_entry, request=request)

        return self.get_response(request)
