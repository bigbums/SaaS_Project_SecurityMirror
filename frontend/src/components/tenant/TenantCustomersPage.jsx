// src/components/tenant/TenantCustomersPage.jsx
import React, { useEffect, useState } from 'react';
import axios from '../../services/tenantAPI';
import { toast } from 'react-toastify';
import { useAuth } from '../../context/AuthContext';
import { can } from '../../utils/privilegeCheck';

const TenantCustomersPage = () => {
  const [customers, setCustomers] = useState([]);
  const { user } = useAuth();

  useEffect(() => {
    axios.get('/customers/')
      .then(res => setCustomers(res.data))
      .catch(() => toast.error('Failed to load customers'));
  }, []);

  const handleAddCustomer = async () => {
    try {
      const name = prompt("Enter customer name:");
      if (!name) return;
      await axios.post('/customers/', { name });
      toast.success('Customer added successfully');
      // Refresh list
      const res = await axios.get('/customers/');
      setCustomers(res.data);
    } catch {
      toast.error('Failed to add customer');
    }
  };

  const handleEditCustomer = async (id, currentName) => {
    try {
      const newName = prompt("Edit customer name:", currentName);
      if (!newName || newName === currentName) return;
      await axios.put(`/customers/${id}/`, { name: newName });
      toast.success('Customer updated successfully');
      // Refresh list
      const res = await axios.get('/customers/');
      setCustomers(res.data);
    } catch {
      toast.error('Failed to update customer');
    }
  };

  const handleDeleteCustomer = async (id) => {
    try {
      await axios.delete(`/customers/${id}/`);
      toast.success('Customer deleted successfully');
      setCustomers(customers.filter(c => c.id !== id));
    } catch {
      toast.error('Failed to delete customer');
    }
  };

  return (
    <div className="customers-page">
      <h2>Customers</h2>

      {/* ✅ Privilege check for Add */}
      {can(user, "customers", "create") && (
        <button className="action-btn" onClick={handleAddCustomer}>
          Add Customer
        </button>
      )}

      <table className="customers-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {customers.map((customer) => (
            <tr key={customer.id}>
              <td>{customer.name}</td>
              <td>
                {/* ✅ Privilege check for Edit */}
                {can(user, "customers", "edit") && (
                  <button
                    className="action-btn"
                    onClick={() => handleEditCustomer(customer.id, customer.name)}
                  >
                    Edit
                  </button>
                )}

                {/* ✅ Privilege check for Delete */}
                {can(user, "customers", "delete") && (
                  <button
                    className="action-btn"
                    onClick={() => handleDeleteCustomer(customer.id)}
                  >
                    Delete
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TenantCustomersPage;
