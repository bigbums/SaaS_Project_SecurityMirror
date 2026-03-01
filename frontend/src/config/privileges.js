export const rolePrivileges = {
  PlatformGlobalAdmin: [
    "tenants:view", "tenants:create", "tenants:edit", "tenants:delete",
    "invoices:view", "invoices:create", "invoices:edit", "invoices:delete",
    "invoices:markPaid", "invoices:resend", "invoices:download",
    "payments:view", "payments:create", "payments:edit", "payments:delete",
    "payments:download", "payments:markReceived",
    "reports:view", "reports:export",
    "settings:managePlatform", "settings:manageStaff", "settings:manageCompliance"
  ],
  PlatformAdmin: [
    "tenants:view", "tenants:create", "tenants:edit", "tenants:delete",
    "users:view", "users:create", "users:edit", "users:delete",
    "tiers:view",
    "invoices:view", // metadata only
    "reports:view", "reports:export",
    "settings:managePlatform", "settings:manageStaff"
  ],
  PlatformStaff: [
    "tenants:view",
    "invoices:view", "invoices:resend", "invoices:download",
    "reports:view"
  ],
  TenantAdmin: [
    "customers:create", "customers:edit", "customers:delete",
    "projects:create", "projects:edit", "projects:close",
    "invoices:create", "invoices:edit", "invoices:delete",
    "invoices:markPaid", "invoices:resend", "invoices:download",
    "payments:view", "payments:create", "payments:edit", "payments:delete",
    "payments:download", "payments:markReceived",
    "reports:view"
  ],
  TenantManager: [
    "customers:view", "customers:create", "customers:edit",
    "projects:view", "projects:create", "projects:edit",
    "invoices:view", "invoices:create", "invoices:markPaid", "invoices:resend", "invoices:download",
    "payments:view", "payments:create", "payments:markReceived", "payments:download",
    "reports:view"
  ],
  TenantStaff: [
    "customers:view",
    "projects:view",
    "invoices:view", "invoices:create", "invoices:download",
    "payments:view", "payments:create", "payments:download"
  ],
  TenantReadOnly: [
    "customers:view",
    "projects:view",
    "invoices:view", "invoices:download",
    "payments:view", "payments:download",
    "reports:view"
  ]
};
