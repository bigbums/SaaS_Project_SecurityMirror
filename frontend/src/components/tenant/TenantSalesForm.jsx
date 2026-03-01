// src/components/tenant/SalesForm.jsx
import React, { useState } from "react";
import axios from "../../services/tenantApi";

const TenantSalesForm = ({ currentTenant, onInvoiceGenerated }) => {
  const [formItems, setFormItems] = useState([{ product_id: "", service_id: "", quantity: 1 }]);

  const addItemRow = () => {
    setFormItems([...formItems, { product_id: "", service_id: "", quantity: 1 }]);
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
        // ✅ This is where you place the snippet
        tenant_id: currentTenant.id,   // dynamic from auth/session
        items: formItems,
      });
      onInvoiceGenerated(res.data);
    } catch (err) {
      console.error("Error creating sale:", err);
    }
  };

  return (
    <section>
      <h2>Record Sale</h2>
      <form onSubmit={handleSale}>
        {formItems.map((item, idx) => (
          <div key={idx} style={{ marginBottom: "1rem" }}>
            <input
              placeholder="Product ID"
              value={item.product_id}
              onChange={e => updateItem(idx, "product_id", e.target.value)}
            />
            <input
              placeholder="Service ID"
              value={item.service_id}
              onChange={e => updateItem(idx, "service_id", e.target.value)}
            />
            <input
              type="number"
              placeholder="Quantity"
              value={item.quantity}
              onChange={e => updateItem(idx, "quantity", e.target.value)}
            />
          </div>
        ))}
        <button type="button" onClick={addItemRow}>+ Add Item</button>
        <button type="submit">Submit Sale</button>
      </form>
    </section>
  );
};

export default TenantSalesForm;
