// src/components/layout/NavMenu.jsx
import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { can } from "../../utils/privilegeCheck";

const NavMenu = ({ type }) => {
  const { user, logout } = useAuth();

  return (
    <nav className="nav-menu">
      <ul>
        {/* Always visible */}
        <li><Link to={`/${type}/overview`}>Overview</Link></li>

        {/* Conditional links based on RBAC */}
        {type === "platform" && can(user, "tenants", "view") && (
          <li><Link to="/platform/tenants">Tenants</Link></li>
        )}

        {can(user, "customers", "view") && type === "tenant" && (
          <li><Link to="/tenant/customers">Customers</Link></li>
        )}

        {can(user, "invoices", "view") && (
          <li><Link to={`/${type}/invoices`}>Invoices</Link></li>
        )}

        {can(user, "reports", "view") && (
          <li><Link to={`/${type}/sales`}>Sales Reports</Link></li>
        )}
      </ul>

      {/* Footer with user info + logout */}
      <div className="nav-footer">
        <span>{user?.name}</span>
        <button onClick={logout}>Logout</button>
      </div>
    </nav>
  );
};

export default NavMenu;
