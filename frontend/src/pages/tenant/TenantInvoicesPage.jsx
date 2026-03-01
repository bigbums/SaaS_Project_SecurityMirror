// src/pages/tenant/Invoices.jsx
import React from 'react';
import TenantInvoiceTable from '../../components/tenant/TenantInvoiceTable';
import Sidebar from '../../components/shared/Sidebar';
import Header from '../../components/shared/Header';
import '../../assets/styles/dashboard.css';

const TenantInvoicesPage = () => {
  return (
    <div className="dashboard-layout">
      {/* Sidebar for tenant navigation */}
      <aside className="dashboard-sidebar">
        <Sidebar role="tenant" />
      </aside>

      {/* Main content area */}
      <main className="dashboard-content">
        <Header title="Tenant Invoices" />
        <section className="content-section">
          {/* ✅ Styled + toast-enabled TenantInvoiceTable */}
          <TenantInvoiceTable />
        </section>
      </main>
    </div>
  );
};

export default TenantInvoicesPage;
