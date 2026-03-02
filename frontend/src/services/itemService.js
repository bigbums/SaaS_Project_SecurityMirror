// frontend/src/services/itemService.js
// src/services/itemService.js
import axios from "axios";

export const getItems = async (endpoint) => {
  const response = await axios.get(`/api/${endpoint}`);
  return response.data;
};

export const createItem = async (endpoint, data) => {
  const response = await axios.post(`/api/${endpoint}`, data);
  return response.data;
};

export const updateItem = async (endpoint, id, updates) => {
  const response = await axios.patch(`/api/${endpoint}/${id}`, updates);
  return response.data;
};

export const deleteItem = async (endpoint, id) => {
  const response = await axios.delete(`/api/${endpoint}/${id}`);
  return response.data;
};

