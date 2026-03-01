// src/context/AuthContext.jsx
import React, { createContext, useContext, useState, useEffect } from "react";
import axios from "axios";
import { rolePrivileges } from "../config/privileges";
import roles from "../config/roles.json";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Fetch user + role from API
    axios.get("/api/auth/me").then(res => {
      const userData = res.data;
      let permissions = [];

      // Normalize permissions from privileges.js
      if (userData.role && rolePrivileges[userData.role]) {
        permissions = rolePrivileges[userData.role];
      }

      // Normalize permissions from roles.json
      if (userData.role && roles[userData.role]) {
        const roleConfig = roles[userData.role];
        Object.keys(roleConfig).forEach(resource => {
          roleConfig[resource].forEach(action => {
            permissions.push(`${resource}:${action}`);
          });
        });
      }

      setUser({ ...userData, permissions });
    });
  }, []);

  // ✅ Logout function
  const logout = async () => {
    try {
      await axios.post("/api/auth/logout"); // backend clears session/token
    } catch (err) {
      console.error("Logout failed:", err);
    }
    setUser(null); // clear user state
    window.location.href = "/login"; // redirect to login page
  };

  return (
    <AuthContext.Provider value={{ user, setUser, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
