// src/utils/privilegeCheck.js
import { rolePrivileges } from '../config/privileges';
import roles from '../config/roles.json';

/**
 * Check if a user can perform a given action on a resource.
 * Works with both string-based privileges ("invoices:download")
 * and structured roles.json ("invoices": ["download"]).
 */
export const can = (user, resource, action) => {
  if (!user) return false;

  // Case 1: user.permissions is an array of strings like "invoices:download"
  if (Array.isArray(user.permissions)) {
    return user.permissions.includes(`${resource}:${action}`);
  }

  // Case 2: user.permissions is an array of objects { resource, action }
  if (user.permissions && user.permissions.some) {
    return user.permissions.some(
      p => p.resource === resource && p.action === action
    );
  }

  // Case 3: fallback to rolePrivileges or roles.json
  if (user.role) {
    const privileges = rolePrivileges[user.role] || [];
    if (privileges.includes(`${resource}:${action}`)) return true;

    const roleConfig = roles[user.role];
    if (roleConfig && roleConfig[resource]) {
      return roleConfig[resource].includes(action);
    }
  }

  return false;
};
