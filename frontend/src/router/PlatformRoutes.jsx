// src/router/PlatformRoutes.jsx
import { Routes, Route } from "react-router-dom";
import PlatformInvoicesPage from "../pages/platform/PlatformInvoicesPage";
import PlatformOverviewPage from "../pages/platform/Overview";
import PlatformTenantsPage from "../pages/platform/Tenants";
import PlatformSalesPage from "../pages/platform/Sales";
import ProtectedRoute from "./ProtectedRoute";

const PlatformRoutes = () => (
  <Routes>
    <Route path="/platform/overview" element={<PlatformOverviewPage />} />

    <Route
      path="/platform/tenants"
      element={
        <ProtectedRoute resource="tenants" action="view">
          <PlatformTenantsPage />
        </ProtectedRoute>
      }
    />

    <Route
      path="/platform/invoices"
      element={
        <ProtectedRoute resource="invoices" action="view">
          <PlatformInvoicesPage />
        </ProtectedRoute>
      }
    />

    <Route
      path="/platform/sales"
      element={
        <ProtectedRoute resource="reports" action="view">
          <PlatformSalesPage />
        </ProtectedRoute>
      }
    />

    {/* fallback */}
    <Route path="*" element={<PlatformOverviewPage />} />
  </Routes>
);

export default PlatformRoutes;
