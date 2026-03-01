# check_fixture.py
from saas_app.core.models import CustomUser, Tenant, TenantUser, SMEProfile, Product, Service, Sale, SaleItem

def run():
    print("\n=== Users ===")
    for u in CustomUser.objects.all():
        print(f"- {u.email} (superuser={u.is_superuser})")

    print("\n=== Tenants ===")
    for t in Tenant.objects.all():
        print(f"- {t.name} (tier={t.tier}, status={t.status})")

    print("\n=== Tenant Users ===")
    for tu in TenantUser.objects.all():
        print(f"- {tu.user.email} -> {tu.tenant.name} ({tu.role})")

    print("\n=== SME Profiles ===")
    for s in SMEProfile.objects.all():
        print(f"- {s.name} (plan={s.subscription_plan}, type={s.type})")

    print("\n=== Products ===")
    for p in Product.objects.all():
        print(f"- {p.name} (${p.price}, stock={p.stock})")

    print("\n=== Services ===")
    for sv in Service.objects.all():
        print(f"- {sv.name} (${sv.price})")

    print("\n=== Sales ===")
    for sale in Sale.objects.all():
        print(f"- {sale.invoice_number} total=${sale.total_amount}")
        for item in sale.items.all():
            print(f"   * {item}")

if __name__ == "__main__":
    run()
