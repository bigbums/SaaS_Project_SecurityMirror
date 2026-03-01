// src/components/tenant/InvoiceCard.jsx
import React from "react";
import { toast } from "react-toastify";
import { initTenantPaystackPayment } from "../../services/tenantAPI";

const TenantInvoiceCard = ({ invoice }) => {
  if (!invoice) return null;

  const handleDownload = () => {
    window.open(
      `http://127.0.0.1:8000/api/invoice/${invoice.invoice_number}/pdf`,
      "_blank"
    );
    toast.info("Downloading invoice PDF...");
  };

  

const handlePay = async () => {
  try {
    const data = await initTenantPaystackPayment(invoice.id);
    if (data.status === "success") {
      window.location.href = data.authorization_url;
    } else {
      toast.error("Payment error: " + data.message);
    }
  } catch (err) {
    toast.error("Unexpected error: " + err.message);
  }
};


  const getCookie = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  };

  return (
    <div className="invoice-card">
      <h2>Invoice</h2>
      <p><strong>Invoice Number:</strong> {invoice.invoice_number}</p>
      <p><strong>Tenant:</strong> {invoice.tenant_name}</p>
      <p><strong>Company:</strong> {invoice.tenant_company}</p>
      <p><strong>Date:</strong> {new Date(invoice.created_at).toLocaleString()}</p>
      <hr />
      <h3>Items</h3>
      <ul>
        {invoice.items.map((item, idx) => (
          <li key={idx}>
            {item.name} — Qty: {item.quantity} — ₦{item.line_total}
          </li>
        ))}
      </ul>
      <hr />
      <h3>Total: ₦{invoice.total_amount}</h3>
      <button
        className="action-btn download-link"
        onClick={handleDownload}
      >
        Download PDF
      </button>
      <button
        className="action-btn paystack-link"
        onClick={handlePay}
      >
        Pay with Paystack
      </button>
    </div>
  );
};

export default TenantInvoiceCard;
