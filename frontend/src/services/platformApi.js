import axios from "axios";

const API_BASE = "/api/platform-invoices"; // Node.js proxy route

// -------------------------------
// CRUD Operations
// -------------------------------
export const getPlatformInvoices = async () => {
  const response = await axios.get(API_BASE);
  return response.data;
};

export const createPlatformInvoice = async (invoiceData) => {
  const response = await axios.post(API_BASE, invoiceData);
  return response.data;
};

export const updatePlatformInvoice = async (id, updates) => {
  const response = await axios.patch(`${API_BASE}/${id}`, updates);
  return response.data;
};

export const deletePlatformInvoice = async (id) => {
  const response = await axios.delete(`${API_BASE}/${id}`);
  return response.data;
};

// -------------------------------
// Payment Methods
// -------------------------------
export const markPlatformInvoicePaid = async (id, payload) => {
  const response = await axios.post(`/api/platform/invoices/${id}/mark-paid/`, payload);
  return response.data;
};

export const recordPlatformTellerPayment = async (id) => {
  const response = await axios.post(`/api/platform/invoices/${id}/teller/`);
  return response.data;
};

export const recordPlatformBankTransfer = async (id) => {
  const response = await axios.post(`/api/platform/invoices/${id}/bank-transfer/`);
  return response.data;
};

export const initPlatformPaystackPayment = async (id) => {
  const response = await axios.post(`/api/platform/paystack-payment/${id}/`);
  return response.data; // { status, authorization_url, payment_id }
};

export const initPlatformOpayPayment = async (id) => {
  const response = await axios.post(`/api/platform/opay-payment/${id}/`);
  return response.data; // { status, authorization_url, payment_id }
};
