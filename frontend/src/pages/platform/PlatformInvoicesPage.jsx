// src/pages/platform/Invoices.jsx
import React from 'react';
import PlatformInvoiceTable from '../../components/platform/PlatformInvoiceTable';
import Sidebar from '../../components/shared/Sidebar';
import Header from '../../components/shared/Header';
import '../../assets/styles/dashboard.css';

const PlatformInvoicesPage = () => {
  return (
    <div className="dashboard-layout">
      {/* Sidebar for platform navigation */}
      <aside className="dashboard-sidebar">
        <Sidebar role="platform" />
      </aside>

      {/* Main content area */}
      <main className="dashboard-content">
        <Header title="Tenant Invoices" />
        <section className="content-section">
          {/* ✅ Styled + toast-enabled PlatformInvoiceTable */}
          <PlatformInvoiceTable />
        </section>
      </main>
    </div>
  );
};

export default PlatformInvoicesPage;
