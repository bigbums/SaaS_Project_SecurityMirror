# Marks saas_app as a Python package
# You can optionally put project-wide initialization code here

default_app_config = "saas_app.apps.SaasAppConfig"

from .celery import app as celery_app

__all__ = ("celery_app",)
