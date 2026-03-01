// src/components/layout/TenantNavbar.jsx
import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { can } from "../../utils/privilegeCheck";

const TenantNavbar = () => {
  const { user, logout } = useAuth();

  return (
    <nav className="tenant-navbar">
      <ul>
        <li><Link to="/tenant/overview">Overview</Link></li>

        {can(user, "customers", "view") && (
          <li><Link to="/tenant/customers">Customers</Link></li>
        )}

        {can(user, "invoices", "view") && (
          <li><Link to="/tenant/invoices">Invoices</Link></li>
        )}

        {can(user, "reports", "view") && (
          <li><Link to="/tenant/sales">Sales Reports</Link></li>
        )}
      </ul>

      <div className="tenant-navbar-footer">
        <span>{user?.name}</span>
        <button onClick={logout}>Logout</button>
      </div>
    </nav>
  );
};

export default TenantNavbar;
