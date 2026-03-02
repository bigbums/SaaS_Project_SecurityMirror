WITH expected AS (
    SELECT 'bunmi.sadiq@acmecorp.com'::text AS email_address, 
           ARRAY['tenant_invite_user','tenant_edit_user','tenant_delete_user',
                 'tenant_view_user','tenant_manage_settings','tenant_view_reports']::text[] AS expected_permissions
    UNION ALL
    SELECT 'adeola.jebutu@acmecorp.com', 
           ARRAY['tenant_invite_user','tenant_edit_user','tenant_view_user','tenant_manage_settings']::text[]
    UNION ALL
    SELECT 'olorundare.ekolo@acmecorp.com', 
           ARRAY['tenant_view_user','tenant_view_reports']::text[]
    UNION ALL
    SELECT 'busari.taoreed@acmecorp.com', 
           ARRAY['tenant_view_user']::text[]
    UNION ALL
    SELECT 'bukola.adewuyi@platform.com', 
           ARRAY['platform_create_tenant','platform_delete_tenant','platform_manage_staff',
                 'platform_manage_settings','platform_view_reports']::text[]
    UNION ALL
    SELECT 'bisola.salawu@platform.com', 
           ARRAY['platform_manage_staff','platform_view_reports']::text[]
    UNION ALL
    SELECT 'grace.davis@platform.com', 
           ARRAY['platform_view_reports']::text[]
),
actual AS (
    SELECT u.email_address,
           ARRAY_AGG(p.name::text ORDER BY p.name) AS actual_permissions
    FROM users u
    JOIN roles r ON u.role_id = r.id
    JOIN role_permissions rp ON r.id = rp.role_id
    JOIN permissions p ON rp.permission_id = p.id
    GROUP BY u.email_address
)
SELECT e.email_address,
       CASE WHEN e.expected_permissions = a.actual_permissions 
            THEN 'PASS' ELSE 'FAIL' END AS validation_result
FROM expected e
LEFT JOIN actual a ON e.email_address = a.email_address
ORDER BY e.email_address;
