from django.db import models
from django.conf import settings

class AuditTrail(models.Model):
    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    object_id = models.PositiveIntegerField()
    object_type = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.timestamp} - {self.user} - {self.action}"
