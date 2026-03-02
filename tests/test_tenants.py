import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_tenant_detail(client, tenant_factory):
    tenant = tenant_factory(name="Tenant A")
    url = reverse("v1:tenant-detail", args=[tenant.id])
    response = client.get(url)
    assert response.status_code == 200
    assert response.json()["name"] == "Tenant A"
