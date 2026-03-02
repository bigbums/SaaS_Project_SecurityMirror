SELECT 
    u.firstname || ' ' || u.lastname AS user_name,
    u.email_address,
    r.name AS role,
    ARRAY_AGG(p.name ORDER BY p.name) AS permissions
FROM users u
JOIN roles r ON u.role_id = r.id
JOIN role_permissions rp ON r.id = rp.role_id
JOIN permissions p ON rp.permission_id = p.id
GROUP BY u.id, u.firstname, u.lastname, u.email_address, r.name
ORDER BY r.name, user_name;
