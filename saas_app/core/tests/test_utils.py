import pytest
from saas_app.core.models import Tier

@pytest.mark.django_db
@pytest.mark.parametrize(
    "tier_name, branding_expected, invoice_expected",
    [
        ("Free", False, False),
        ("Standard", True, False),
        ("Premium", True, True),
        ("Enterprise", True, True),
    ],
)
def test_has_feature_by_tier(tier_name, branding_expected, invoice_expected):
    tier = Tier.objects.get(name=tier_name)
    features = tier.features or []

    assert ("branding" in features) == branding_expected
    # ✅ match seed data: invoice_customization instead of invoice
    assert ("invoice_customization" in features) == invoice_expected
