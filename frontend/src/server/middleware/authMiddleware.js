// src/server/middleware/authMiddleware.js
import jwt from "jsonwebtoken";
import { rolePrivileges } from "../../config/privileges.js";
import roles from "../../config/roles.json" assert { type: "json" };

export const authMiddleware = (req, res, next) => {
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return res.status(401).json({ error: "Unauthorized: missing token" });
  }

  const token = authHeader.split(" ")[1];

  try {
    // Verify JWT (issued by your auth service)
    const decoded = jwt.verify(token, process.env.JWT_SECRET);

    // Attach user info
    let user = {
      id: decoded.id,
      email: decoded.email,
      role: decoded.role,
      permissions: [],
    };

    // Normalize permissions from privileges.js
    if (user.role && rolePrivileges[user.role]) {
      user.permissions = [...rolePrivileges[user.role]];
    }

    // Normalize permissions from roles.json
    if (user.role && roles[user.role]) {
      const roleConfig = roles[user.role];
      Object.keys(roleConfig).forEach((resource) => {
        roleConfig[resource].forEach((action) => {
          user.permissions.push(`${resource}:${action}`);
        });
      });
    }

    // Attach enriched user to request
    req.user = user;

    next();
  } catch (err) {
    return res.status(401).json({ error: "Unauthorized: invalid token" });
  }
};
