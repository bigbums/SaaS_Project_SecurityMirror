// src/pages/tenant/Overview.jsx
import React from "react";
import { useAuth } from "../../context/AuthContext";
import { can } from "../../utils/privilegeCheck";

const TenantOverviewPage = () => {
  const { user } = useAuth();

  return (
    <div className="tenant-overview">
      <h1>Tenant Dashboard</h1>

      {/* Always visible */}
      <section>
        <h2>Welcome, {user?.name}</h2>
        <p>Here’s an overview of your tenant activity.</p>
      </section>

      {/* RBAC-controlled widgets */}
      {can(user, "customers", "view") && (
        <section>
          <h2>Customers Overview</h2>
          <p>Summary of customer accounts and activity.</p>
        </section>
      )}

      {can(user, "projects", "view") && (
        <section>
          <h2>Projects Overview</h2>
          <p>Active projects and milestones.</p>
        </section>
      )}

      {can(user, "invoices", "view") && (
        <section>
          <h2>Invoices Summary</h2>
          <p>Recent invoices and outstanding balances.</p>
        </section>
      )}

      {can(user, "reports", "view") && (
        <section>
          <h2>Reports Snapshot</h2>
          <p>Latest tenant performance and sales reports.</p>
        </section>
      )}
    </div>
  );
};

export default TenantOverviewPage;
