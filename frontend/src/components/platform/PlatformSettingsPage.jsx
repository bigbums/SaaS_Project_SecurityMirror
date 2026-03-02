// src/components/platform/PlatformSettingsPage.jsx
import React, { useEffect, useState } from "react";
import axios from "../../services/platformApi";
import { toast } from "react-toastify";
import { useAuth } from "../../context/AuthContext";
import { can } from "../../utils/privilegeCheck";

const PlatformSettingsPage = () => {
  const [settings, setSettings] = useState({});
  const [staff, setStaff] = useState([]);
  const { user } = useAuth();

  useEffect(() => {
    // Load platform settings
    axios.get("/settings/")
      .then(res => setSettings(res.data))
      .catch(() => toast.error("Failed to load platform settings"));

    // Load staff list
    axios.get("/staff/")
      .then(res => setStaff(res.data))
      .catch(() => toast.error("Failed to load staff"));
  }, []);

  const handleUpdateSettings = async () => {
    try {
      const newConfig = prompt("Enter new platform config JSON:", JSON.stringify(settings));
      if (!newConfig) return;
      await axios.put("/settings/", JSON.parse(newConfig));
      toast.success("Platform settings updated successfully");
      const res = await axios.get("/settings/");
      setSettings(res.data);
    } catch {
      toast.error("Failed to update settings");
    }
  };

  const handleAddStaff = async () => {
    try {
      const name = prompt("Enter staff name:");
      if (!name) return;
      await axios.post("/staff/", { name });
      toast.success("Staff added successfully");
      const res = await axios.get("/staff/");
      setStaff(res.data);
    } catch {
      toast.error("Failed to add staff");
    }
  };

  const handleRemoveStaff = async (id) => {
    try {
      await axios.delete(`/staff/${id}/`);
      toast.success("Staff removed successfully");
      setStaff(staff.filter(s => s.id !== id));
    } catch {
      toast.error("Failed to remove staff");
    }
  };

  return (
    <section>
      <h2>Platform Settings</h2>

      {/* ✅ Privilege check for managing platform settings */}
      {can(user, "settings", "managePlatform") ? (
        <div className="settings-section">
          <pre>{JSON.stringify(settings, null, 2)}</pre>
          <button className="action-btn" onClick={handleUpdateSettings}>
            Update Settings
          </button>
        </div>
      ) : (
        <p>You do not have permission to manage platform settings.</p>
      )}

      <h2>Staff Management</h2>

      {/* ✅ Privilege check for managing staff */}
      {can(user, "settings", "manageStaff") ? (
        <div className="staff-section">
          <button className="action-btn" onClick={handleAddStaff}>
            Add Staff
          </button>
          <ul>
            {staff.map(s => (
              <li key={s.id}>
                {s.name}
                <button
                  className="action-btn"
                  onClick={() => handleRemoveStaff(s.id)}
                >
                  Remove
                </button>
              </li>
            ))}
          </ul>
        </div>
      ) : (
        <p>You do not have permission to manage staff.</p>
      )}
    </section>
  );
};

export default PlatformSettingsPage;
