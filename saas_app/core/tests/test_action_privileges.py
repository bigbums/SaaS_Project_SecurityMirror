# saas_app/core/tests/test_action_privileges.py

import pytest
from saas_app.core.viewsets.viewsets import TenantInvoiceViewSet, PlatformInvoiceViewSet

@pytest.mark.parametrize("action,expected_privilege", [
    ("create", "invoice:create"),
    ("update", "invoice:update"),
    ("partial_update", "invoice:update"),
    ("destroy", "invoice:delete"),
    ("mark_paid", "invoice:update"),
    ("download", "invoice:view"),
    ("resend", "invoice:view"),
    ("list", "invoice:view"),
    ("retrieve", "invoice:view"),
])
def test_tenant_invoice_action_privileges(action, expected_privilege):
    viewset = TenantInvoiceViewSet()
    viewset.action = action
    assert viewset.get_required_privilege() == expected_privilege


@pytest.mark.parametrize("action,expected_privilege", [
    ("create", "invoice:create"),
    ("update", "invoice:update"),
    ("partial_update", "invoice:update"),
    ("destroy", "invoice:delete"),
    ("mark_paid", "invoice:update"),
    ("download", "invoice:view"),
    ("resend", "invoice:view"),
    ("list", "invoice:view"),
    ("retrieve", "invoice:view"),
])
def test_platform_invoice_action_privileges(action, expected_privilege):
    viewset = PlatformInvoiceViewSet()
    viewset.action = action
    assert viewset.get_required_privilege() == expected_privilege
