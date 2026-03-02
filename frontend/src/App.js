import React, { useEffect, useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import TenantInvoicePaymentOptions from "./components/tenant/TenantInvoicePaymentOptions";
import PlatformInvoicePaymentOptions from "./components/platform/PlatformInvoicePaymentOptions";

function App() {
  const [projects, setProjects] = useState([]);
  const [invoice, setInvoice] = useState(null);
  const [formItems, setFormItems] = useState([{ product_id: "", service_id: "", quantity: 1 }]);

  // Fetch projects on load
  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/projects")
      .then(res => res.json())
      .then(data => setProjects(data.projects))
      .catch(err => console.error("Error fetching projects:", err));
  }, []);

  // Handle sale creation
  const handleSale = (e) => {
    e.preventDefault();
    fetch("http://127.0.0.1:8000/api/sales/create", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sme_profile_id: 1,   // later this can be dynamic per tenant
        items: formItems
      })
    })
      .then(res => res.json())
      .then(data => setInvoice(data));
  };

  // Add new item row
  const addItemRow = () => {
    setFormItems([...formItems, { product_id: "", service_id: "", quantity: 1 }]);
  };

  // Update item row
  const updateItem = (index, field, value) => {
    const updated = [...formItems];
    updated[index][field] = value;
    setFormItems(updated);
  };

  return (
    <Router>
      <Routes>
        {/* Default route: your current SME Sales & Inventory Tool */}
        <Route
          path="/"
          element={
            <div style={{ fontFamily: "Arial", margin: "2rem" }}>
              <h1>SME Sales & Inventory Tool</h1>

              {/* Projects Section */}
              <h2>Projects</h2>
              <ul>
                {projects.map(p => (
                  <li key={p.id}>
                    {p.name} — <strong>{p.status}</strong>
                  </li>
                ))}
              </ul>

              {/* Sales Form */}
              <h2>Record Sale</h2>
              <form onSubmit={handleSale}>
                {formItems.map((item, idx) => (
                  <div key={idx} style={{ marginBottom: "1rem" }}>
                    <input
                      placeholder="Product ID"
                      value={item.product_id}
                      onChange={e => updateItem(idx, "product_id", e.target.value)}
                      style={{ marginRight: "0.5rem" }}
                    />
                    <input
                      placeholder="Service ID"
                      value={item.service_id}
                      onChange={e => updateItem(idx, "service_id", e.target.value)}
                      style={{ marginRight: "0.5rem" }}
                    />
                    <input
                      type="number"
                      placeholder="Quantity"
                      value={item.quantity}
                      onChange={e => updateItem(idx, "quantity", e.target.value)}
                      style={{ width: "80px" }}
                    />
                  </div>
                ))}
                <button type="button" onClick={addItemRow}>+ Add Item</button>
                <button type="submit" style={{ marginLeft: "1rem" }}>Submit Sale</button>
              </form>

         {/* Invoice Display */}
{/* Invoice Display */}
{invoice && (
  <div style={{
    border: "1px solid #ccc",
    padding: "1rem",
    marginTop: "2rem",
    maxWidth: "500px",
    backgroundColor: "#f9f9f9"
  }}>
    <h2 style={{ textAlign: "center" }}>Invoice</h2>
    <p><strong>Invoice Number:</strong> {invoice.invoice_number}</p>
    <p><strong>SME Profile:</strong> {invoice.sme_profile}</p>
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

    {/* Paid invoices */}
    {invoice.status === "paid" && (
      <p style={{ color: "green", fontWeight: "bold", textAlign: "center" }}>
        ✅ This invoice has already been paid.
      </p>
    )}

{/* Pending invoices */}
{invoice.status === "pending" && (
  <div style={{ marginTop: "1rem", textAlign: "center" }}>
    <p style={{ color: "orange", fontWeight: "bold" }}>
      ⏳ Payment is pending confirmation. Options are temporarily disabled.
    </p>

    <button disabled>
  🧾 Teller
  <LoadingSpinner size={14} color="orange" />
</button>


    <div style={{ display: "flex", justifyContent: "center", gap: "0.5rem", flexWrap: "wrap" }}>
      <button
        disabled
        title={invoice.pending_reason === "cash" ? "Awaiting cash confirmation" : "Payment pending confirmation"}
        style={{
          padding: "0.5rem 1rem",
          backgroundColor: invoice.pending_reason === "cash" ? "#ffe5b4" : "#ccc",
          color: invoice.pending_reason === "cash" ? "#000" : "#666",
          borderRadius: "4px",
          border: invoice.pending_reason === "cash" ? "2px solid orange" : "none",
          cursor: "not-allowed"
        }}
      >
        💵 Cash
        {invoice.pending_reason === "cash" && <span className="spinner"></span>}
      </button>

      <button
        disabled
        title={invoice.pending_reason === "teller" ? "Awaiting teller slip upload" : "Payment pending confirmation"}
        style={{
          padding: "0.5rem 1rem",
          backgroundColor: invoice.pending_reason === "teller" ? "#ffe5b4" : "#ccc",
          color: invoice.pending_reason === "teller" ? "#000" : "#666",
          borderRadius: "4px",
          border: invoice.pending_reason === "teller" ? "2px solid orange" : "none",
          cursor: "not-allowed"
        }}
      >
        🧾 Teller
        {invoice.pending_reason === "teller" && <span className="spinner"></span>}
      </button>

      <button
        disabled
        title={invoice.pending_reason === "bank-transfer" ? "Awaiting bank transfer confirmation" : "Payment pending confirmation"}
        style={{
          padding: "0.5rem 1rem",
          backgroundColor: invoice.pending_reason === "bank-transfer" ? "#ffe5b4" : "#ccc",
          color: invoice.pending_reason === "bank-transfer" ? "#000" : "#666",
          borderRadius: "4px",
          border: invoice.pending_reason === "bank-transfer" ? "2px solid orange" : "none",
          cursor: "not-allowed"
        }}
      >
        🏦 Bank Transfer
        {invoice.pending_reason === "bank-transfer" && <span className="spinner"></span>}
      </button>

      <button
        disabled
        title={invoice.pending_reason === "paystack" ? "Awaiting Paystack verification" : "Payment pending confirmation"}
        style={{
          padding: "0.5rem 1rem",
          backgroundColor: invoice.pending_reason === "paystack" ? "#ffe5b4" : "#ccc",
          color: invoice.pending_reason === "paystack" ? "#000" : "#666",
          borderRadius: "4px",
          border: invoice.pending_reason === "paystack" ? "2px solid orange" : "none",
          cursor: "not-allowed"
        }}
      >
        💳 Paystack
        {invoice.pending_reason === "paystack" && <span className="spinner"></span>}
      </button>

      <button
        disabled
        title={invoice.pending_reason === "opay" ? "Awaiting Opay verification" : "Payment pending confirmation"}
        style={{
          padding: "0.5rem 1rem",
          backgroundColor: invoice.pending_reason === "opay" ? "#ffe5b4" : "#ccc",
          color: invoice.pending_reason === "opay" ? "#000" : "#666",
          borderRadius: "4px",
          border: invoice.pending_reason === "opay" ? "2px solid orange" : "none",
          cursor: "not-allowed"
        }}
      >
        📱 Opay
        {invoice.pending_reason === "opay" && <span className="spinner"></span>}
      </button>
    </div>
  </div>
)}





    {/* Unpaid invoices */}
    {invoice.status === "unpaid" && (
      <div style={{ marginTop: "1rem", textAlign: "center" }}>
        <h3>Pay This Invoice</h3>

        {invoice.type === "tenant" && (
          <div>
            <h4 style={{ marginBottom: "0.5rem" }}>Tenant Payment Options</h4>
            <div style={{ display: "flex", justifyContent: "center", gap: "0.5rem", flexWrap: "wrap" }}>
              <a href={`/tenant/invoices/${invoice.id}/pay?method=cash`} style={{ padding: "0.5rem 1rem", backgroundColor: "#6c757d", color: "#fff", borderRadius: "4px", textDecoration: "none" }}>💵 Cash</a>
              <a href={`/tenant/invoices/${invoice.id}/pay?method=teller`} style={{ padding: "0.5rem 1rem", backgroundColor: "#ffc107", color: "#000", borderRadius: "4px", textDecoration: "none" }}>🧾 Teller</a>
              <a href={`/tenant/invoices/${invoice.id}/pay?method=bank-transfer`} style={{ padding: "0.5rem 1rem", backgroundColor: "#17a2b8", color: "#fff", borderRadius: "4px", textDecoration: "none" }}>🏦 Bank Transfer</a>
              <a href={`/tenant/invoices/${invoice.id}/pay?method=paystack`} style={{ padding: "0.5rem 1rem", backgroundColor: "#007bff", color: "#fff", borderRadius: "4px", textDecoration: "none" }}>💳 Paystack</a>
              <a href={`/tenant/invoices/${invoice.id}/pay?method=opay`} style={{ padding: "0.5rem 1rem", backgroundColor: "#28a745", color: "#fff", borderRadius: "4px", textDecoration: "none" }}>📱 Opay</a>
            </div>
          </div>
        )}

        {invoice.type === "platform" && (
          <div>
            <h4 style={{ marginBottom: "0.5rem" }}>Platform Payment Options</h4>
            <div style={{ display: "flex", justifyContent: "center", gap: "0.5rem", flexWrap: "wrap" }}>
              <a href={`/platform/invoices/${invoice.id}/pay?method=cash`} style={{ padding: "0.5rem 1rem", backgroundColor: "#6c757d", color: "#fff", borderRadius: "4px", textDecoration: "none" }}>💵 Cash</a>
              <a href={`/platform/invoices/${invoice.id}/pay?method=teller`} style={{ padding: "0.5rem 1rem", backgroundColor: "#ffc107", color: "#000", borderRadius: "4px", textDecoration: "none" }}>🧾 Teller</a>
              <a href={`/platform/invoices/${invoice.id}/pay?method=bank-transfer`} style={{ padding: "0.5rem 1rem", backgroundColor: "#17a2b8", color: "#fff", borderRadius: "4px", textDecoration: "none" }}>🏦 Bank Transfer</a>
              <a href={`/platform/invoices/${invoice.id}/pay?method=paystack`} style={{ padding: "0.5rem 1rem", backgroundColor: "#007bff", color: "#fff", borderRadius: "4px", textDecoration: "none" }}>💳 Paystack</a>
              <a href={`/platform/invoices/${invoice.id}/pay?method=opay`} style={{ padding: "0.5rem 1rem", backgroundColor: "#28a745", color: "#fff", borderRadius: "4px", textDecoration: "none" }}>📱 Opay</a>
            </div>
          </div>
        )}
      </div>
    )}
  </div>
)}




              {invoice && (
                <a
                  href={`http://127.0.0.1:8000/api/invoice/${invoice.invoice_number}/pdf`}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Download PDF
                </a>
              )}
            </div>
          }
        />

        {/* Tenant Payment Options */}
        <Route path="/tenant/invoices/:id/pay" element={<TenantInvoicePaymentOptions />} />

        {/* Platform Payment Options */}
        <Route path="/platform/invoices/:id/pay" element={<PlatformInvoicePaymentOptions />} />
      </Routes>
    </Router>
  );
}

export default App;
