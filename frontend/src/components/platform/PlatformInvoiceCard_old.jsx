// src/components/platform/InvoiceCard.jsx
import React from "react";
import { toast } from "react-toastify";
import { useAuth } from "../../context/AuthContext";
import { can } from "../../utils/privilegeCheck";

const PlatformInvoiceCard = ({ invoice }) => {
  const { user } = useAuth();

  if (!invoice) return null;

  const handleDownload = () => {
    window.open(
      `http://127.0.0.1:8000/api/platform/invoice/${invoice.invoice_number}/pdf`,
      "_blank"
    );
    toast.info("Downloading tenant invoice PDF...");
  };

  return (
    <div className="invoice-card">
      <h2>Platform Invoice</h2>
      <p><strong>Invoice Number:</strong> {invoice.invoice_number}</p>
      <p><strong>Tenant:</strong> {invoice.tenant_name}</p>
      <p><strong>Company:</strong> {invoice.tenant_company}</p>
      <p><strong>Date:</strong> {new Date(invoice.created_at).toLocaleString()}</p>
      <hr />
      <h3>Items</h3>
      <ul>
        {invoice.items.map((item, idx) => (
          <li key={idx}>
            Tenant: {item.tenant_name} — Amount: ₦{item.amount}
          </li>
        ))}
      </ul>
      <hr />
      <h3>Total: ₦{invoice.total_amount}</h3>

      {/* ✅ Privilege check for Download */}
      {can(user, "invoices", "download") && (
        <button
          className="action-btn download-link"
          onClick={handleDownload}
        >
          Download PDF
        </button>
      )}
    </div>
  );
};

export default PlatformInvoiceCard;
