// src/components/tenant/ProjectsList.jsx
import React, { useEffect, useState } from "react";
import axios from "../../services/tenantApi";
import { toast } from "react-toastify";
import { useAuth } from "../../context/AuthContext";
import { can } from "../../utils/privilegeCheck";

const TenantProjectsList = () => {
  const [projects, setProjects] = useState([]);
  const { user } = useAuth();

  useEffect(() => {
    axios.get("/projects/")
      .then(res => setProjects(res.data.projects))
      .catch(err => toast.error("Error fetching projects"));
  }, []);

  const refreshProjects = async () => {
    const res = await axios.get("/projects/");
    setProjects(res.data.projects);
  };

  const handleCreateProject = async () => {
    try {
      const name = prompt("Enter new project name:");
      if (!name) return;
      await axios.post("/projects/", { name });
      toast.success("Project created successfully");
      refreshProjects();
    } catch {
      toast.error("Failed to create project");
    }
  };

  const handleEditProject = async (id, currentName) => {
    try {
      const newName = prompt("Edit project name:", currentName);
      if (!newName || newName === currentName) return;
      await axios.put(`/projects/${id}/`, { name: newName });
      toast.success("Project updated successfully");
      refreshProjects();
    } catch {
      toast.error("Failed to update project");
    }
  };

  const handleCloseProject = async (id) => {
    try {
      await axios.put(`/projects/${id}/close/`);
      toast.success("Project closed successfully");
      refreshProjects();
    } catch {
      toast.error("Failed to close project");
    }
  };

  return (
    <section>
      <h2>Projects</h2>

      {/* ✅ Privilege check for Create */}
      {can(user, "projects", "create") && (
        <button className="action-btn" onClick={handleCreateProject}>
          New Project
        </button>
      )}

      <ul>
        {projects.map(p => (
          <li key={p.id}>
            {p.name} — <strong>{p.status}</strong>
            <div className="actions">
              {/* ✅ Privilege check for Edit */}
              {can(user, "projects", "edit") && (
                <button
                  className="action-btn"
                  onClick={() => handleEditProject(p.id, p.name)}
                >
                  Edit
                </button>
              )}

              {/* ✅ Privilege check for Close */}
              {can(user, "projects", "close") && p.status !== "Closed" && (
                <button
                  className="action-btn"
                  onClick={() => handleCloseProject(p.id)}
                >
                  Close
                </button>
              )}
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
};

export default TenantProjectsList;
