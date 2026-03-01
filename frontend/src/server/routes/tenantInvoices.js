// src/server/routes/tenantInvoices.js
import express from "express";
import axios from "axios";
import { can } from "../../utils/privilegeCheck";

const router = express.Router();

// Middleware to enforce RBAC
const requirePrivilege = (resource, action) => (req, res, next) => {
  const user = req.user; // assume user injected by auth middleware

  if (!user || !can(user, resource, action)) {
    return res.status(403).json({ error: "Forbidden: insufficient privileges" });
  }

  next();
};

// GET invoices (view privilege required)
router.get("/", requirePrivilege("invoices", "view"), async (req, res) => {
  try {
    const response = await axios.get(`${process.env.DJANGO_API}/tenant-invoices`, {
      headers: { Authorization: req.headers.authorization },
    });
    res.json(response.data);
  } catch {
    res.status(500).json({ error: "Failed to fetch invoices" });
  }
});

// Download invoice (download privilege required)
router.get("/:id/pdf", requirePrivilege("invoices", "download"), async (req, res) => {
  try {
    const response = await axios.get(
      `${process.env.DJANGO_API}/tenant-invoices/${req.params.id}/pdf/`,
      { headers: { Authorization: req.headers.authorization }, responseType: "arraybuffer" }
    );
    res.setHeader("Content-Type", "application/pdf");
    res.send(response.data);
  } catch {
    res.status(500).json({ error: "Failed to download invoice" });
  }
});

// Resend invoice (resend privilege required)
router.post("/:id/resend", requirePrivilege("invoices", "resend"), async (req, res) => {
  try {
    const response = await axios.post(
      `${process.env.DJANGO_API}/tenant-invoices/${req.params.id}/resend`,
      {},
      { headers: { Authorization: req.headers.authorization } }
    );
    res.json(response.data);
  } catch {
    res.status(500).json({ error: "Failed to resend invoice" });
  }
});

// Mark invoice as paid (markPaid privilege required)
router.patch("/:id/markPaid", requirePrivilege("invoices", "markPaid"), async (req, res) => {
  try {
    const response = await axios.patch(
      `${process.env.DJANGO_API}/tenant-invoices/${req.params.id}/`,
      { status: "paid" },
      { headers: { Authorization: req.headers.authorization } }
    );
    res.json(response.data);
  } catch {
    res.status(500).json({ error: "Failed to mark invoice as paid" });
  }
});

// Delete invoice (delete privilege required)
router.delete("/:id", requirePrivilege("invoices", "delete"), async (req, res) => {
  try {
    await axios.delete(`${process.env.DJANGO_API}/tenant-invoices/${req.params.id}/`, {
      headers: { Authorization: req.headers.authorization },
    });
    res.json({ success: true });
  } catch {
    res.status(500).json({ error: "Failed to delete invoice" });
  }
});

export default router;
