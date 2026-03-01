// src/components/tenant/TenantInvoiceTable.jsx
import React, { useEffect, useState } from "react";
import { toast } from "react-toastify";
import { useAuth } from "../../context/AuthContext";
import { can } from "../../utils/privilegeCheck";
import { getItems, updateItem } from "../../services/itemService"; // generic service
import { initTenantPaystackPayment } from "../../services/tenantAPI";

const TenantInvoiceTable = () => {
  const [invoices, setInvoices] = useState([]);
  const { user } = useAuth();

  useEffect(() => {
    fetchInvoices();
  }, []);

  const fetchInvoices = async () => {
    try {
      const data = await getItems("tenant-invoices"); // Node.js proxy route
      setInvoices(data);
    } catch {
      toast.error("Failed to load invoices");
    }
  };

  const handleDownload = (id) => {
    window.open(`/api/tenant-invoices/${id}/pdf/`, "_blank");
    toast.info("Downloading invoice...");
  };

  const handleResend = async (id) => {
    try {
      await updateItem("tenant-invoices", id, { action: "resend" });
      toast.success("Invoice resent successfully");
    } catch {
      toast.error("Failed to resend invoice");
    }
  };

  const handleMarkPaid = async (id) => {
    try {
      await updateItem("tenant-invoices", id, { status: "paid" });
      toast.success("Invoice marked as paid");
      fetchInvoices();
    } catch {
      toast.error("Failed to update invoice");
    }
  };



const handlePay = async (id) => {
  try {
    const data = await initTenantPaystackPayment(id);
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
    <table className="invoice-table">
      <thead>
        <tr>
          <th>Invoice #</th>
          <th>Customer</th>
          <th>Amount</th>
          <th>Status</th>
          <th>Due Date</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {invoices.map((invoice) => (
          <tr key={invoice.id}>
            <td>{invoice.number}</td>
            <td>{invoice.customer_name}</td>
            <td>₦{invoice.amount}</td>
            <td className={`status ${invoice.status.toLowerCase()}`}>
              {invoice.status}
            </td>
            <td>{invoice.due_date}</td>
            <td>
              {can(user, "invoices", "download") && (
                <button
                  className="action-btn"
                  onClick={() => handleDownload(invoice.id)}
                >
                  Download
                </button>
              )}
              {can(user, "invoices", "resend") && (
                <button
                  className="action-btn"
                  onClick={() => handleResend(invoice.id)}
                >
                  Resend
                </button>
              )}
              {can(user, "invoices", "markPaid") &&
                invoice.status.toLowerCase() !== "paid" && (
                  <button
                    className="action-btn"
                    onClick={() => handleMarkPaid(invoice.id)}
                  >
                    Mark Paid
                  </button>
                )}
              {invoice.status.toLowerCase() !== "paid" && (
                <button
                  className="action-btn paystack-link"
                  onClick={() => handlePay(invoice.id)}
                >
                  Pay with Paystack
                </button>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default TenantInvoiceTable;
