// src/pages/platform/Overview.jsx
import React from "react";
import { useAuth } from "../../context/AuthContext";
import { can } from "../../utils/privilegeCheck";

const PlatformOverviewPage = () => {
  const { user } = useAuth();

  return (
    <div className="platform-overview">
      <h1>Platform Dashboard</h1>

      {/* Always visible */}
      <section>
        <h2>Welcome, {user?.name}</h2>
        <p>Here’s an overview of your platform activity.</p>
      </section>

      {/* RBAC-controlled widgets */}
      {can(user, "tenants", "view") && (
        <section>
          <h2>Tenants Overview</h2>
          <p>Summary of tenant accounts and activity.</p>
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
          <p>Latest sales and performance reports.</p>
        </section>
      )}
    </div>
  );
};

export default PlatformOverviewPage;
