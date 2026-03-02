// src/pages/tenant/Sales.jsx
import React, { useState } from 'react';
import TenantProjectsList from '../../components/tenant/ProjectsList';
import TenantSalesForm from '../../components/tenant/SalesForm';
import InvoiceCard from '../../components/tenant/InvoiceCard';
import Sidebar from '../../components/shared/Sidebar';
import Header from '../../components/shared/Header';
import '../../assets/styles/dashboard.css';

const TenantSalesPage = ({ currentTenant }) => {
  const [invoice, setInvoice] = useState(null);

  return (
    <div className="dashboard-layout">
      {/* Sidebar for tenant navigation */}
      <aside className="dashboard-sidebar">
        <Sidebar role="tenant" />
      </aside>

      {/* Main content area */}
      <main className="dashboard-content">
        <Header title="Tenant Sales" />
        <section className="content-section">
          {/* Tenant projects list */}
          <TenantProjectsList />

          {/* Sales form that generates invoice */}
          <TenantSalesForm currentTenant={currentTenant} onInvoiceGenerated={setInvoice} />

          {/* Invoice detail card appears after sale */}
          <InvoiceCard invoice={invoice} />
        </section>
      </main>
    </div>
  );
};

export default TenantSalesPage;
