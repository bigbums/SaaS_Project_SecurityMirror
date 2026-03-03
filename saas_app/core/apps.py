from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "saas_app.core"
    label = "core"  # 👈 defines the app_label

    def ready(self):
        """
        Import signal handlers to ensure they are registered
        when the app is loaded by Django.
        """
        # Import signals module (safe, one-way dependency)
        import saas_app.core.signals
