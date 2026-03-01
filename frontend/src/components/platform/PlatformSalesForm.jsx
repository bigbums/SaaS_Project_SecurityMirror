// src/components/platform/SalesForm.jsx
import React, { useState } from "react";
import axios from "../../services/platformApi";

const PlatformSalesForm = ({ currentPlatform, onInvoiceGenerated }) => {
  const [formItems, setFormItems] = useState([{ tenant_id: "", amount: 0 }]);

  const addItemRow = () => {
    setFormItems([...formItems, { tenant_id: "", amount: 0 }]);
  };

  const updateItem = (index, field, value) => {
    const updated = [...formItems];
    updated[index][field] = value;
    setFormItems(updated);
  };

  const handleSale = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post("/sales/create", {
        // ✅ Platform issues invoices to tenants
        platform_id: currentPlatform.id,   // dynamic from auth/session
        items: formItems,
      });
      onInvoiceGenerated(res.data);
    } catch (err) {
      console.error("Error creating platform sale:", err);
    }
  };

  return (
    <section>
      <h2>Record Tenant Billing</h2>
      <form onSubmit={handleSale}>
        {formItems.map((item, idx) => (
          <div key={idx} style={{ marginBottom: "1rem" }}>
            <input
              placeholder="Tenant ID"
              value={item.tenant_id}
              onChange={e => updateItem(idx, "tenant_id", e.target.value)}
            />
            <input
              type="number"
              placeholder="Amount"
              value={item.amount}
              onChange={e => updateItem(idx, "amount", e.target.value)}
            />
          </div>
        ))}
        <button type="button" onClick={addItemRow}>+ Add Tenant</button>
        <button type="submit">Submit Billing</button>
      </form>
    </section>
  );
};

export default PlatformSalesForm;
