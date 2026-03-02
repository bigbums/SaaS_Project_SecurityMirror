// src/pages/UnauthorizedPage.jsx
import React from "react";
import { Link } from "react-router-dom";

const UnauthorizedPage = () => {
  return (
    <div className="unauthorized-page">
      <h1>Access Denied</h1>
      <p>
        You do not have the required privileges to view this page.
        Please contact your administrator if you believe this is an error.
      </p>
      <Link to="/" className="back-link">
        Return to Dashboard
      </Link>
    </div>
  );
};

export default UnauthorizedPage;
