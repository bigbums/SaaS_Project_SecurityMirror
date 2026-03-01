import os
from pathlib import Path
import logging
from logging.handlers import TimedRotatingFileHandler
import json



BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-2$k%#m+%(06lpl#^r9=m98bh7-p@kekelwv$)c4mn4^^x2m82+'
DEBUG = True
ALLOWED_HOSTS = []

# Company branding
PLATFORM_COMPANY_NAME = "Bumys Cloud"


INSTALLED_APPS = [
    # Default Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'corsheaders',
    'django_crontab',
    "rest_framework",
    "rest_framework.authtoken",


    # Local apps
    'core.apps.CoreConfig',
    'accounts.apps.AccountsConfig',
    'audit.apps.AuditConfig',  # ✅ use the AppConfig class for audit
]


LOGOUT_REDIRECT_URL = "home"  # or "home" if you want to send users to your homepage


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "corsheaders.middleware.CorsMiddleware", 
    "django.middleware.common.CommonMiddleware",

    # Custom middlewares
    #"core.middleware.TenantMiddleware",
  # Custom middlewares
    "saas_app.core.middleware.TenantMiddleware.TenantMiddleware",   # attaches tenant
    "saas_app.core.middleware.rbac_middleware.RBACMiddleware",      # attaches permissions
    "saas_app.core.middleware.correlation.CorrelationIdMiddleware", # correlation ID
    "saas_app.core.middleware.audit.AuditLoggingMiddleware", # automatic request audit
]

ROOT_URLCONF = 'saas_app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'saas_app.wsgi.application'

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

# Deny unauthorized access
handler403 = "core.views.custom_permission_denied"


# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"

# Global static files directory (in addition to app-specific static folders like core/static)
STATICFILES_DIRS = [
    BASE_DIR / "core" / "static"
    ]

# Custom user model
AUTH_USER_MODEL = "accounts.CustomUser"


# Default Company Information
DEFAULT_LOGO = "/static/core/default_logo.png"
DEFAULT_ADDRESS = "123 Default Business Street, Lagos"
DEFAULT_PHONE = "+234 800 000 0000"
DEFAULT_EMAIL = "support@ourplatform.com"

# Paystack Keys
PAYSTACK_SECRET_KEY = "sk_test_xxxxx"  # replace with your secret key
PAYSTACK_PUBLIC_KEY = "pk_test_xxxxx"  # replace with your public key


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

#FIXTURE_DIRS = [
#   BASE_DIR / "core" / "fixtures",
#]




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
            "format": "[{asctime}] {levelname} {name} [CID:{correlation_id}] {message}",
            "style": "{",
        },
        "json": {
            "()": JSONFormatter,   # ✅ use custom JSON formatter
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "filters": ["correlation_id"],
        },
        "audit_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "audit.log"),
            "when": "D",
            "interval": 90,
            "backupCount": 4,
            "formatter": "json",
            "filters": ["correlation_id"],
        },
        "security_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "security.log"),
            "when": "D",
            "interval": 90,
            "backupCount": 4,
            "formatter": "json",
            "filters": ["correlation_id"],
        },
        "invoice_file": {   # ✅ new handler
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "invoice.log"),
            "when": "D",
            "interval": 90,
            "backupCount": 4,
            "formatter": "json",
            "filters": ["correlation_id"],
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "audit": {
            "handlers": ["audit_file"],
            "level": "INFO",
            "propagate": False,
        },
        "security": {
            "handlers": ["security_file"],
            "level": "WARNING",
            "propagate": False,
        },
        "invoice": {   # ✅ new logger
            "handlers": ["invoice_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
