// src/components/platform/PlatformTenantsPage.jsx
import React, { useEffect, useState } from "react";
import axios from "../../services/platformAPI";
import { toast } from "react-toastify";
import { useAuth } from "../../context/AuthContext";
import { can } from "../../utils/privilegeCheck";

const PlatformTenantsPage = () => {
  const [tenants, setTenants] = useState([]);
  const { user } = useAuth();

  useEffect(() => {
    axios.get("/tenants/")
      .then(res => setTenants(res.data))
      .catch(() => toast.error("Failed to load tenants"));
  }, []);

  const refreshTenants = async () => {
    const res = await axios.get("/tenants/");
    setTenants(res.data);
  };

  const handleAddTenant = async () => {
    try {
      const name = prompt("Enter tenant name:");
      if (!name) return;
      await axios.post("/tenants/", { name });
      toast.success("Tenant added successfully");
      refreshTenants();
    } catch {
      toast.error("Failed to add tenant");
    }
  };

  const handleEditTenant = async (id, currentName) => {
    try {
      const newName = prompt("Edit tenant name:", currentName);
      if (!newName || newName === currentName) return;
      await axios.put(`/tenants/${id}/`, { name: newName });
      toast.success("Tenant updated successfully");
      refreshTenants();
    } catch {
      toast.error("Failed to update tenant");
    }
  };

  const handleDeleteTenant = async (id) => {
    try {
      await axios.delete(`/tenants/${id}/`);
      toast.success("Tenant deleted successfully");
      setTenants(tenants.filter(t => t.id !== id));
    } catch {
      toast.error("Failed to delete tenant");
    }
  };

  return (
    <section>
      <h2>Platform Tenants</h2>

      {/* ✅ Privilege check for Add */}
      {can(user, "tenants", "create") && (
        <button className="action-btn" onClick={handleAddTenant}>
          Add Tenant
        </button>
      )}

      <table className="tenants-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Company</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {tenants.map((tenant) => (
            <tr key={tenant.id}>
              <td>{tenant.name}</td>
              <td>{tenant.company}</td>
              <td>
                {/* ✅ Privilege check for Edit */}
                {can(user, "tenants", "edit") && (
                  <button
                    className="action-btn"
                    onClick={() => handleEditTenant(tenant.id, tenant.name)}
                  >
                    Edit
                  </button>
                )}

                {/* ✅ Privilege check for Delete */}
                {can(user, "tenants", "delete") && (
                  <button
                    className="action-btn"
                    onClick={() => handleDeleteTenant(tenant.id)}
                  >
                    Delete
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
};

export default PlatformTenantsPage;
