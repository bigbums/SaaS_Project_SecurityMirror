// src/components/platform/PlatformInvoiceTable.jsx
import React, { useEffect, useState } from "react";
import { toast } from "react-toastify";
import { useAuth } from "../../context/AuthContext";
import { can } from "../../utils/privilegeCheck";
import {
  getPlatformInvoices,
  updatePlatformInvoice,
  deletePlatformInvoice,
} from "../../services/platformApi";
import { initPlatformPaystackPayment } from "../../services/platformApi";

const PlatformInvoiceTable = () => {
  const [invoices, setInvoices] = useState([]);
  const { user } = useAuth();

  useEffect(() => {
    fetchInvoices();
  }, []);

  const fetchInvoices = async () => {
    try {
      const data = await getPlatformInvoices();
      setInvoices(data);
    } catch {
      toast.error("Failed to load platform invoices");
    }
  };

  const handleDownload = (id) => {
    window.open(`/api/platform-invoices/${id}/pdf/`, "_blank");
    toast.info("Downloading platform invoice...");
  };

  const handleResend = async (id) => {
    try {
      await updatePlatformInvoice(id, { action: "resend" });
      toast.success("Platform invoice resent successfully");
    } catch {
      toast.error("Failed to resend platform invoice");
    }
  };

  const handleMarkPaid = async (id) => {
    try {
      await updatePlatformInvoice(id, { status: "paid" });
      toast.success("Platform invoice marked as paid");
      fetchInvoices();
    } catch {
      toast.error("Failed to update platform invoice");
    }
  };

  const handleDelete = async (id) => {
    try {
      await deletePlatformInvoice(id);
      toast.success("Platform invoice deleted successfully");
      fetchInvoices();
    } catch {
      toast.error("Failed to delete platform invoice");
    }
  };

 

const handlePay = async (id) => {
  try {
    const data = await initPlatformPaystackPayment(id);
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
          <th>Tenant</th>
          <th>Company</th>
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
            <td>{invoice.tenant_name}</td>
            <td>{invoice.tenant_company}</td>
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
              {can(user, "invoices", "delete") && (
                <button
                  className="action-btn"
                  onClick={() => handleDelete(invoice.id)}
                >
                  Delete
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

export default PlatformInvoiceTable;
