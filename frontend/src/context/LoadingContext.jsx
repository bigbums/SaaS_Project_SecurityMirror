import React, { createContext, useState, useContext } from "react";

const LoadingContext = createContext();

export const LoadingProvider = ({ children }) => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  // Helper functions
  const startLoading = (msg) => {
    setLoading(true);
    setMessage(msg);
  };

  const stopLoading = () => {
    setLoading(false);
    setMessage("");
  };

  return (
    <LoadingContext.Provider value={{ loading, message, startLoading, stopLoading }}>
      {children}
    </LoadingContext.Provider>
  );
};

// Custom hook for easy access
export const useLoading = () => useContext(LoadingContext);
