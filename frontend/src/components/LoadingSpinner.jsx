import React from "react";
import "./App.css";

const LoadingSpinner = ({ size = 40, color = "orange", fullscreen = false, message = "" }) => {
  if (fullscreen) {
    return (
      <div style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100vw",
        height: "100vh",
        backgroundColor: "rgba(0,0,0,0.3)",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        zIndex: 9999
      }}>
        <span
          className="spinner"
          style={{
            width: size,
            height: size,
            border: `4px solid rgba(255, 165, 0, 0.3)`,
            borderTop: `4px solid ${color}`,
          }}
        />
        {message && (
          <p style={{ marginTop: "1rem", color: "#fff", fontWeight: "bold", fontSize: "1.2rem" }}>
            {message}
          </p>
        )}
      </div>
    );
  }

  return (
    <span
      className="spinner"
      style={{
        width: size,
        height: size,
        border: `2px solid rgba(255, 165, 0, 0.3)`,
        borderTop: `2px solid ${color}`,
      }}
    />
  );
};

export default LoadingSpinner;
