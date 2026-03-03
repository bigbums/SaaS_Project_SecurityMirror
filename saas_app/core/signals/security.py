import logging
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.utils.timezone import now
from saas_app.core.utils.logging_helpers import log_json

security_logger = logging.getLogger("security")

def log_failed_login(sender, credentials, request, **kwargs):
    log_entry = {
        "event": "failed_login",
        "message": "failed login attempt",
        "user": credentials.get("username"),
        "ip": request.META.get("REMOTE_ADDR"),
        "path": request.path,
    }
    log_json(security_logger, "warning", log_entry, request=request)

user_login_failed.connect(log_failed_login)

def update_login(sender, user, request, **kwargs):
    if hasattr(user, "tenantuser"):
        user.tenantuser.last_login = now()
        user.tenantuser.save()
    if hasattr(user, "platformuser"):
        user.platformuser.last_login = now()
        user.platformuser.save()

def update_logout(sender, user, request, **kwargs):
    if hasattr(user, "tenantuser"):
        user.tenantuser.last_logout = now()
        user.tenantuser.save()
    if hasattr(user, "platformuser"):
        user.platformuser.last_logout = now()
        user.platformuser.save()

user_logged_in.connect(update_login)
user_logged_out.connect(update_logout)
