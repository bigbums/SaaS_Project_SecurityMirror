import requests
import time
from django.conf import settings
from saas_app.core.utils.payments import create_payment, record_payment
from saas_app.core.utils.emails import send_invoice_email

def initiate_paystack(tenant, tier, request):
    amount = tier.price * 100
    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
    data = {
        "email": tenant.email,
        "amount": amount,
        "callback_url": request.build_absolute_uri("/payment/paystack/callback/"),
    }
    response = requests.post("https://api.paystack.co/transaction/initialize", json=data, headers=headers)
    res_data = response.json()
    if res_data.get("status"):
        ref = res_data["data"]["reference"]
        create_payment(tenant, tier, amount, ref, "paystack")
        return res_data["data"]["authorization_url"]
    return None

def verify_paystack(reference):
    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
    response = requests.get(f"https://api.paystack.co/transaction/verify/{reference}", headers=headers)
    res_data = response.json()
    success = res_data.get("status") and res_data["data"]["status"] == "success"
    return success

def initiate_opay(tenant, tier, request):
    amount = tier.price * 100
    ref = f"opay_{tenant.id}_{tier.id}_{int(time.time())}"
    headers = {"Authorization": f"Bearer {settings.OPAY_SECRET_KEY}"}
    data = {
        "amount": amount,
        "currency": "NGN",
        "reference": ref,
        "returnUrl": request.build_absolute_uri("/payment/opay/callback/"),
        "userInfo": {"email": tenant.email},
    }
    response = requests.post("https://testapi.opaycheckout.com/api/v1/international/payment/create", json=data, headers=headers)
    res_data = response.json()
    if res_data.get("code") == "0000":
        create_payment(tenant, tier, amount, ref, "opay")
        return res_data["data"]["cashierUrl"]
    return None

def verify_opay(reference):
    headers = {"Authorization": f"Bearer {settings.OPAY_SECRET_KEY}"}
    response = requests.get("https://testapi.opaycheckout.com/api/v1/international/cashier/status", headers=headers)
    res_data = response.json()
    success = res_data.get("status") and res_data["data"]["status"] == "SUCCESS"
    return success
