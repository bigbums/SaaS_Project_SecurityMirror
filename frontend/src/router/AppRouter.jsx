// src/router/AppRouter.jsx
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import PlatformRoutes from "./PlatformRoutes";
import TenantRoutes from "./TenantRoutes";
import UnauthorizedPage from "../pages/UnauthorizedPage";
import LoginPage from "../pages/LoginPage";

const AppRouter = () => (
  <Router>
    <Routes>
      {/* Mount platform and tenant route groups */}
      <Route path="/*" element={<PlatformRoutes />} />
      <Route path="/*" element={<TenantRoutes />} />

      {/* Global routes */}
      <Route path="/unauthorized" element={<UnauthorizedPage />} />
      <Route path="/login" element={<LoginPage />} />
    </Routes>
  </Router>
);

export default AppRouter;
