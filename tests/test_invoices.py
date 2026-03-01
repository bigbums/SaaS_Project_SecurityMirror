import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_tenant_invoice_list(client, invoice_factory):
    invoice_factory(amount=500)
    url = reverse("v1:tenantinvoice-list")
    response = client.get(url)
    assert response.status_code == 200
