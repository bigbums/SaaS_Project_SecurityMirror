import pytest
from django.utils import timezone
from saas_app.core.models import PlatformInvoice, TenantInvoice

@pytest.mark.django_db
class TestInvoiceRefunds:
    @pytest.mark.parametrize(
        "model,endpoint_template,fixture_names,initial_status,expected_codes",
        [
            # Platform invoice cases
            (PlatformInvoice, "/api/v1/platform-invoices/{id}/mark_paid/", 
             ["platform_user"], "paid", [200, 403]),
            (PlatformInvoice, "/api/v1/platform-invoices/{id}/mark_paid/", 
             ["platform_user"], "unpaid", [400, 403]),
            (PlatformInvoice, "/api/v1/platform-invoices/{id}/mark_paid/", 
             ["platform_user"], "overdue", [400, 403]),

            # Tenant invoice cases
            (TenantInvoice, "/api/v1/tenants/{tenant_id}/invoices/{id}/", 
             ["tenant_and_user", "tenant_customer"], "paid", [200, 403]),
            (TenantInvoice, "/api/v1/tenants/{tenant_id}/invoices/{id}/", 
             ["tenant_and_user", "tenant_customer"], "unpaid", [400, 403]),
            (TenantInvoice, "/api/v1/tenants/{tenant_id}/invoices/{id}/", 
             ["tenant_and_user", "tenant_customer"], "overdue", [400, 403]),
        ]
    )
    def test_refund_invoice(
        self,
        api_client,
        model,
        endpoint_template,
        fixture_names,
        initial_status,
        expected_codes,
        request
    ):
        # Dynamically pull fixtures
        fixtures = {name: request.getfixturevalue(name) for name in fixture_names}

        # Tenant setup
        tenant = None
        custom_user = None
        if "tenant_and_user" in fixtures:
            tenant, tenant_user, custom_user = fixtures["tenant_and_user"]
            api_client.force_authenticate(user=custom_user)

        if "platform_user" in fixtures:
            platform_user = fixtures["platform_user"]
            custom_user = platform_user.user
            api_client.force_authenticate(user=custom_user)

        # Create invoice depending on model type
        if model is PlatformInvoice:
            invoice = model.objects.create(
                tenant=tenant,
                status=initial_status,
                amount=200,
                currency="USD",
                due_date=timezone.now().date(),
            )
            endpoint = endpoint_template.format(id=invoice.id)
        else:  # TenantInvoice
            invoice = model.objects.create(
                tenant=tenant,
                customer=fixtures["tenant_customer"],
                status=initial_status,
                amount=150,
                currency="USD",
                due_date=timezone.now().date(),
            )
            endpoint = endpoint_template.format(tenant_id=tenant.id, id=invoice.id)

        # PATCH request to update status
        response = api_client.patch(endpoint, {"status": "paid"}, format="json")
        invoice.refresh_from_db()

        assert response.status_code in expected_codes
        if response.status_code == 200:
            assert invoice.status == "paid"
