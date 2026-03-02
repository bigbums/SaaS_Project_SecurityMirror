// src/pages/platform/Sales.jsx
import React, { useState } from "react";
import PlatformProjectsList from "../../components/platform/ProjectsList";
import PlatformSalesForm from "./PlatformSalesForm";
import PlatformInvoiceCard from "./PlatformInvoiceCard";

const PlatformSalesPage = ({ currentPlatform }) => {
  const [invoice, setInvoice] = useState(null);

  return (
    <div className="dashboard-layout">
      <PlatformProjectsList />
      <PlatformSalesForm currentPlatform={currentPlatform} onInvoiceGenerated={setInvoice} />
      <PlatformInvoiceCard invoice={invoice} />
    </div>
  );
};

export default PlatformSalesPage;
