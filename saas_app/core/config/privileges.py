role_privileges = {
    # Tenant roles
    "owner": [
        "invoice:view", "invoice:create", "invoice:update", "invoice:delete",
        "invoice:mark_paid", "invoice:download_pdf", "invoice:send_reminder",
        "customer:view", "customer:create", "customer:update", "customer:delete",
        "user:manage",
        "billing:manage",
        "location:manage"
    ],
    "admin": [
        "invoice:view",   # ✅ only view
        "customer:view"
    ],
    "manager": [
        "invoice:view", "invoice:update",   # ✅ can update, not create
        "customer:view"
    ],
    "viewer": [
        "invoice:view",
        "customer:view"
    ],
    "user": [
        "invoice:view", "invoice:create",
        "customer:view"
    ],

    # Platform roles
    "platform_owner": [
        "tenant:create", "tenant:update", "tenant:delete",
        "platform_user:manage", "platform_setting:update", "report:view",
        "invoice:view", "invoice:create", "invoice:update", "invoice:delete"
    ],
    "platform_admin": [
        "tenant:view", "tenant:update", "platform_setting:update", "platform_user:manage",
        "report:view",
        "invoice:view", "invoice:create"   # ✅ admins can create at platform level
    ],
    "platform_manager": [
        "tenant:view", "report:view",
        "invoice:view", "invoice:update"
    ],
    "platform_user": [
        "tenant:view",
        "invoice:view", "invoice:create"
    ],
}
