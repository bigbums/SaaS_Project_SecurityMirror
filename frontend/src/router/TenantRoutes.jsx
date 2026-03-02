// src/router/TenantRoutes.jsx
import { Routes, Route } from "react-router-dom";
import TenantOverviewPage from "../pages/tenant/Overview";
import TenantCustomersPage from "../pages/tenant/Customers";
import TenantInvoicesPage from "../pages/tenant/TenantInvoicesPage";
import TenantSalesPage from "../pages/tenant/Sales";
import ProtectedRoute from "./ProtectedRoute";

const TenantRoutes = () => (
  <Routes>
    <Route path="/tenant/overview" element={<TenantOverviewPage />} />

    <Route
      path="/tenant/customers"
      element={
        <ProtectedRoute resource="customers" action="view">
          <TenantCustomersPage />
        </ProtectedRoute>
      }
    />

    <Route
      path="/tenant/invoices"
      element={
        <ProtectedRoute resource="invoices" action="view">
          <TenantInvoicesPage />
        </ProtectedRoute>
      }
    />

    <Route
      path="/tenant/sales"
      element={
        <ProtectedRoute resource="reports" action="view">
          <TenantSalesPage />
        </ProtectedRoute>
      }
    />

    {/* fallback */}
    <Route path="*" element={<TenantOverviewPage />} />
  </Routes>
);

export default TenantRoutes;
