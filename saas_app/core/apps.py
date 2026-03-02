from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "saas_app.core"
    label = "core" # 👈 this defines the app_label

    def ready(self):
        import saas_app.core.signals  # ✅ ensures signals are registered


