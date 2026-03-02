// src/components/platform/PlatformReportsPage.jsx
import React, { useEffect, useState } from "react";
import axios from "../../services/platformApi";
import { toast } from "react-toastify";
import { useAuth } from "../../context/AuthContext";
import { can } from "../../utils/privilegeCheck";

const PlatformReportsPage = () => {
  const [reports, setReports] = useState([]);
  const { user } = useAuth();

  useEffect(() => {
    axios.get("/reports/")
      .then(res => setReports(res.data))
      .catch(() => toast.error("Failed to load reports"));
  }, []);

  const handleExport = async (id) => {
    try {
      const res = await axios.get(`/reports/${id}/export/`, { responseType: "blob" });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `report_${id}.pdf`);
      document.body.appendChild(link);
      link.click();
      toast.success("Report exported successfully");
    } catch {
      toast.error("Failed to export report");
    }
  };

  return (
    <section>
      <h2>Platform Reports</h2>
      <table className="reports-table">
        <thead>
          <tr>
            <th>Report Name</th>
            <th>Created At</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {reports.map((report) => (
            <tr key={report.id}>
              <td>{report.name}</td>
              <td>{new Date(report.created_at).toLocaleString()}</td>
              <td>
                {/* ✅ Privilege check for View */}
                {can(user, "reports", "view") && (
                  <button
                    className="action-btn"
                    onClick={() => toast.info(`Viewing report: ${report.name}`)}
                  >
                    View
                  </button>
                )}

                {/* ✅ Privilege check for Export */}
                {can(user, "reports", "export") && (
                  <button
                    className="action-btn"
                    onClick={() => handleExport(report.id)}
                  >
                    Export
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

export default PlatformReportsPage;
