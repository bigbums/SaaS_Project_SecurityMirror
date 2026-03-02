# saas_app/core/tests/mixins.py
import pytest
from saas_app.core.constants import VALID_CURRENCIES

class CurrencyTestMixin:
    # Valid + invalid currency codes
    currency_cases = [
        *[(code, 201) for code in VALID_CURRENCIES],   # all valid codes
        ("XYZ", 400), ("ABC", 400), ("123", 400), ("ZZZ", 400)  # invalid codes
    ]

    @pytest.mark.parametrize("currency,expected_status", currency_cases)
    def test_currency_codes(self, currency, expected_status):
        # Subclasses must implement `create_invoice` and `test_user`
        response = self.create_invoice(user=self.test_user, currency=currency)
        assert response.status_code == expected_status
