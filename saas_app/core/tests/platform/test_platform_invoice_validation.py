from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from saas_app.core.constants import VALID_CURRENCIES
from saas_app.core.tests.base import BasePlatformTestCase


class TestPlatformInvoiceValidation(BasePlatformTestCase):

    def test_invoice_field_validations(self):
        self.client.force_authenticate(user=self.platform_owner)
        url = reverse("v1:platforminvoice-list")
        today = timezone.now().date()

        cases = [
            ("customer", {
                "tenant": self.tenant.id,   # ✅ added tenant
                "amount": 200,
                "currency": "USD",
                "due_date": (today + timedelta(days=1)).isoformat(),
                "status": "unpaid",
            }, 400, "Customer is required"),

            ("tenant", {
                "customer": self.customer.id,
                "amount": 200,
                "currency": "USD",
                "due_date": (today + timedelta(days=1)).isoformat(),
                "status": "unpaid",
            }, 400, "Tenant is required"),

            ("amount", {
                "tenant": self.tenant.id,   # ✅ added tenant
                "customer": self.customer.id,
                "currency": "USD",
                "due_date": (today + timedelta(days=1)).isoformat(),
                "status": "unpaid",
            }, 400, "Amount is required"),

            ("currency", {
                "tenant": self.tenant.id,   # ✅ added tenant
                "customer": self.customer.id,
                "amount": 200,
                "due_date": (today + timedelta(days=1)).isoformat(),
                "status": "unpaid",
            }, 400, "Currency is required"),

            ("due_date", {
                "tenant": self.tenant.id,   # ✅ added tenant
                "customer": self.customer.id,
                "amount": 200,
                "currency": "USD",
                "status": "unpaid",
            }, 400, "Due date is required"),

            ("currency", {
                "tenant": self.tenant.id,   # ✅ added tenant
                "customer": self.customer.id,
                "amount": 200,
                "currency": "XYZ",
                "due_date": (today + timedelta(days=1)).isoformat(),
                "status": "unpaid",
            }, 400, "Invalid currency code."),

            ("due_date", {
                "tenant": self.tenant.id,   # ✅ added tenant
                "customer": self.customer.id,
                "amount": 200,
                "currency": "USD",
                "due_date": (today - timedelta(days=1)).isoformat(),
                "status": "unpaid",
            }, 400, "Due date cannot be in the past."),

            ("optional_fields", {
                "tenant": self.tenant.id,   # ✅ added tenant
                "customer": self.customer.id,
                "amount": 200,
                "currency": "USD",
                "due_date": (today + timedelta(days=1)).isoformat(),
                "status": "unpaid",
            }, 201, None),
        ]

        for field, payload, expected_status, expected_message in cases:
            with self.subTest(field=field):
                response = self.client.post(url, payload, format="json")
                self.assertEqual(response.status_code, expected_status)
                if expected_status == 400:
                    self.assertEqual(response.data[field][0], expected_message)

    def test_valid_currencies(self):
        self.client.force_authenticate(user=self.platform_owner)
        url = reverse("v1:platforminvoice-list")
        today = timezone.now().date()
        for code in VALID_CURRENCIES:
            with self.subTest(currency=code):
                payload = {
                    "tenant": self.tenant.id,   # ✅ added tenant
                    "customer": self.customer.id,
                    "amount": 200,
                    "currency": code,
                    "due_date": (today + timedelta(days=1)).isoformat(),
                    "status": "unpaid",
                    "description": f"Invoice in {code}"
                }
                response = self.client.post(url, payload, format="json")
                self.assertEqual(response.status_code, 201)


class TestPlatformInvoiceCurrencies(BasePlatformTestCase):

    def test_currency_codes(self):
        self.client.force_authenticate(user=self.platform_owner)
        url = reverse("v1:platforminvoice-list")
        today = timezone.now().date()

        cases = [(code, 201) for code in VALID_CURRENCIES] + [
            ("XYZ", 400), ("ABC", 400), ("123", 400), ("ZZZ", 400)
        ]

        for currency, expected_status in cases:
            with self.subTest(currency=currency):
                payload = {
                    "tenant": self.tenant.id,   # ✅ added tenant
                    "customer": self.customer.id,
                    "amount": 200,
                    "currency": currency,
                    "due_date": (today + timedelta(days=1)).isoformat(),
                    "status": "unpaid",
                    "description": f"Invoice in {currency}"
                }
                response = self.client.post(url, payload, format="json")
                self.assertEqual(response.status_code, expected_status)
                if expected_status == 400:
                    self.assertEqual(response.data["currency"][0], "Invalid currency code.")
