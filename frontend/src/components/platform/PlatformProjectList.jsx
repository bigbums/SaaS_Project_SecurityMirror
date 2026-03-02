// src/components/platform/ProjectsList.jsx
import React, { useEffect, useState } from "react";
import axios from "../../services/platformApi";

const PlatformProjectsList = () => {
  const [projects, setProjects] = useState([]);

  useEffect(() => {
    axios.get("/projects/")
      .then(res => setProjects(res.data.projects))
      .catch(err => console.error("Error fetching platform projects:", err));
  }, []);

  return (
    <section>
      <h2>Tenant Projects</h2>
      <ul>
        {projects.map(p => (
          <li key={p.id}>
            {p.name} — <strong>{p.status}</strong> (Tenant: {p.tenant_name})
          </li>
        ))}
      </ul>
    </section>
  );
};

export default PlatformProjectsList;
