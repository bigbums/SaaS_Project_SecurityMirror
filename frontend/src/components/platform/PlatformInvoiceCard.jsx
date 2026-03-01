// src/components/platform/PlatformInvoicesPage.jsx
import React, { useEffect, useState } from "react";
import axios from "../../services/platformApi";
import { toast } from "react-toastify";
import { useAuth } from "../../context/AuthContext";
import { can } from "../../utils/privilegeCheck";

const PlatformInvoicesPage = () => {
  const [invoices, setInvoices] = useState([]);
  const { user } = useAuth();

  useEffect(() => {
    axios.get("/invoices/")
      .then(res => setInvoices(res.data))
      .catch(() => toast.error("Failed to load platform invoices"));
  }, []);

  const handleResend = async (id) => {
    try {
      await axios.post(`/invoices/${id}/resend/`);
      toast.success("Invoice resent successfully");
    } catch {
      toast.error("Failed to resend invoice");
    }
  };

  const handleDelete = async (id) => {
    try {
      await axios.delete(`/invoices/${id}/`);
      toast.success("Invoice deleted successfully");
      setInvoices(invoices.filter(inv => inv.id !== id));
    } catch {
      toast.error("Failed to delete invoice");
    }
  };

  const handlePay = async (id) => {
    try {
      const response = await axios.post(`/platform/paystack-payment/${id}/`);
      const data = response.data;
      if (data.status === "success") {
        window.location.href = data.authorization_url;
      } else {
        toast.error("Payment error: " + data.message);
      }
    } catch (err) {
      toast.error("Unexpected error: " + err.message);
    }
  };

  return (
    <section>
      <h2>Platform Invoices</h2>
      <table className="invoice-table">
        <thead>
          <tr>
            <th>Invoice #</th>
            <th>Tenant</th>
            <th>Amount</th>
            <th>Status</th>
            <th>Due Date</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {invoices.map(inv => (
            <tr key={inv.id}>
              <td>{inv.number}</td>
              <td>{inv.tenant_name}</td>
              <td>₦{inv.amount}</td>
              <td className={`status ${inv.status.toLowerCase()}`}>{inv.status}</td>
              <td>{inv.due_date}</td>
              <td>
                {can(user, "invoices", "resend") && (
                  <button className="action-btn" onClick={() => handleResend(inv.id)}>
                    Resend
                  </button>
                )}
                {can(user, "invoices", "delete") && (
                  <button className="action-btn" onClick={() => handleDelete(inv.id)}>
                    Delete
                  </button>
                )}
                {inv.status.toLowerCase() !== "paid" && (
                  <button className="action-btn paystack-link" onClick={() => handlePay(inv.id)}>
                    Pay with Paystack
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
};

export default PlatformInvoicesPage;
