import axios from "axios";

const API_BASE = "/api/tenant-invoices"; // Node.js proxy route

// -------------------------------
// CRUD Operations
// -------------------------------
export const getTenantInvoices = async () => {
  const response = await axios.get(API_BASE);
  return response.data;
};

export const createTenantInvoice = async (invoiceData) => {
  const response = await axios.post(API_BASE, invoiceData);
  return response.data;
};

export const updateTenantInvoice = async (id, updates) => {
  const response = await axios.patch(`${API_BASE}/${id}`, updates);
  return response.data;
};

export const deleteTenantInvoice = async (id) => {
  const response = await axios.delete(`${API_BASE}/${id}`);
  return response.data;
};

// -------------------------------
// Payment Methods
// -------------------------------
export const markTenantInvoicePaid = async (id, payload) => {
  const response = await axios.post(`/api/tenant/invoices/${id}/mark-paid/`, payload);
  return response.data;
};

export const recordTenantTellerPayment = async (id) => {
  const response = await axios.post(`/api/tenant/invoices/${id}/teller/`);
  return response.data;
};

export const recordTenantBankTransfer = async (id) => {
  const response = await axios.post(`/api/tenant/invoices/${id}/bank-transfer/`);
  return response.data;
};

export const initTenantPaystackPayment = async (id) => {
  const response = await axios.post(`/api/tenant/paystack-payment/${id}/`);
  return response.data; // { status, authorization_url, payment_id }
};

export const initTenantOpayPayment = async (id) => {
  const response = await axios.post(`/api/tenant/opay-payment/${id}/`);
  return response.data; // { status, authorization_url, payment_id }
};
