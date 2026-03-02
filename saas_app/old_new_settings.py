import os
from pathlib import Path
import logging
from logging.handlers import TimedRotatingFileHandler
import json

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "your-secret-key"
DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    # Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party apps
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "django_crontab",

    # Local apps
    "saas_app.core",
    "saas_app.accounts",
    "saas_app.audit",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    # Custom middlewares
    "saas_app.core.middleware.TenantMiddleware.TenantMiddleware",   # attaches tenant
    "saas_app.core.middleware.rbac_middleware.RBACMiddleware",      # attaches permissions
    "saas_app.core.middleware.correlation.CorrelationIdMiddleware", # correlation ID
    "saas_app.core.middleware.audit.AuditLoggingMiddleware",        # automatic request audit
]

ROOT_URLCONF = "saas_app.urls"
WSGI_APPLICATION = "saas_app.wsgi.application"
ASGI_APPLICATION = "saas_app.asgi.application"

# Error handlers
handler403 = "saas_app.core.views.custom_permission_denied"

# Static files
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "saas_app" / "core" / "static"
]

# Paystack configuration
# These will read from environment variables if set, otherwise fall back to placeholders
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY", "sk_test_placeholder")
PAYSTACK_PUBLIC_KEY = os.getenv("PAYSTACK_PUBLIC_KEY", "pk_test_placeholder")

# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "correlation_id": {
            "()": "saas_app.core.logging_filters.CorrelationIdFilter",
        },
    },
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "filters": ["correlation_id"],
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # you can create a templates/ folder
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

AUTH_USER_MODEL = "accounts.CustomUser"

# Company branding
PLATFORM_COMPANY_NAME = "Bumys Cloud"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'saas_db',
        'USER': 'postgres',
        'PASSWORD': '123456',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

DJANGO_ENV = os.getenv("DJANGO_ENV", "development")

if DJANGO_ENV == "production":
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = "in-v3.mailjet.com"
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = "your_mailjet_api_key"
    EMAIL_HOST_PASSWORD = "your_mailjet_secret_key"
    DEFAULT_FROM_EMAIL = "your_verified_email@example.com"
else:
    EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
    EMAIL_FILE_PATH = BASE_DIR / "sent_emails"
    DEFAULT_FROM_EMAIL = "no-reply@example.com"

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]


LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# Default Company Information
DEFAULT_LOGO = "/static/core/default_logo.png"
DEFAULT_ADDRESS = "123 Default Business Street, Lagos"
DEFAULT_PHONE = "+234 800 000 0000"
DEFAULT_EMAIL = "support@ourplatform.com"

# Defaults keyed by PLANS

PLAN_DEFAULTS = {
    "Free": {"max_users": 1, "max_locations": 1, "price": 0},
    "Standard": {"max_users": 10, "max_locations": 2, "price": 0},
    "Premium": {"max_users": 50, "max_locations": 10, "price": 5000},
    "Enterprise": {"max_users": 200, "max_locations": 50, "price": 20000},
}

PLAN_FEATURES = {
    "Free": [],
    "Standard": ["branding"],
    "Premium": ["branding", "invoice_customization"],
    "Enterprise": ["branding", "invoice_customization"],
}


REST_FRAMEWORK = {

    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],

        "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",        
        "rest_framework.authentication.TokenAuthentication",  # optional if you want token-based auth
    ],
}

CRONJOBS = [
    # Every Monday at 9 AM
    ('0 9 * * MON', 'django.core.management.call_command', ['export_sales_chart']),
]

CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"

LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "correlation_id": getattr(record, "correlation_id", "none"),
            "message": record.getMessage(),
        }
        return json.dumps(log_entry)

# 👇 RBAC and role privilege configs
with open(os.path.join(BASE_DIR, "saas_app/core/config/roles.json")) as f:
    ROLES_CONFIG = json.load(f)

from saas_app.core.config.privileges import role_privileges

