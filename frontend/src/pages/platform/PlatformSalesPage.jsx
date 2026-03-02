// src/pages/platform/Sales.jsx
import React, { useState } from 'react';
import PlatformProjectsList from '../../components/platform/ProjectsList';
import PlatformSalesForm from '../../components/platform/SalesForm';
import PlatformInvoiceCard from '../../components/platform/InvoiceCard';
import Sidebar from '../../components/shared/Sidebar';
import Header from '../../components/shared/Header';
import '../../assets/styles/dashboard.css';

const PlatformSalesPage = ({ currentPlatform }) => {
  const [invoice, setInvoice] = useState(null);

  return (
    <div className="dashboard-layout">
      {/* Sidebar for platform navigation */}
      <aside className="dashboard-sidebar">
        <Sidebar role="platform" />
      </aside>

      {/* Main content area */}
      <main className="dashboard-content">
        <Header title="Platform Billing" />
        <section className="content-section">
          {/* Platform projects list (tenants) */}
          <PlatformProjectsList />

          {/* Billing form that generates tenant invoice */}
          <PlatformSalesForm currentPlatform={currentPlatform} onInvoiceGenerated={setInvoice} />

          {/* Invoice detail card appears after billing */}
          <PlatformInvoiceCard invoice={invoice} />
        </section>
      </main>
    </div>
  );
};

export default PlatformSalesPage;
