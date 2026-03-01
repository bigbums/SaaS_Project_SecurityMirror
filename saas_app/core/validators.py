from rest_framework import serializers
from saas_app.core.models import Currency

def validate_currency(value: str) -> str:
    if not Currency.objects.filter(code=value, active=True).exists():
        raise serializers.ValidationError(f"Invalid or inactive currency code: {value}")
    return value
