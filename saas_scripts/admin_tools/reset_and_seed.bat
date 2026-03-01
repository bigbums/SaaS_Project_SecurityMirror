@echo off
cd /d C:\Users\DELL\saas_app

:: Yellow for warning
color 0E
echo [!] WARNING: This will FLUSH the database, SEED data, DUMP fixtures, and RELOAD them.
set /p confirm="Are you sure you want to continue? (Y/N): "

if /I "%confirm%"=="Y" (
    :: Cyan for action
    color 0B
    echo 🔄 Flushing database...
    python manage.py flush --no-input
    if %ERRORLEVEL% NEQ 0 (
        color 0C
        echo [✗] ERROR: Flush failed.
        goto end
    )

    echo 🌱 Seeding database with sample data (timezone-aware)...
    python seed_data.py
    if %ERRORLEVEL% NEQ 0 (
        color 0C
        echo [✗] ERROR: Seeding failed.
        goto end
    )

    echo 💾 Dumping seeded data into fixture (UTF-8, no BOM)...
    python manage.py dumpdata core.CustomUser core.SMEProfile core.Tenant core.TenantUser --indent 2 > core\fixtures\initial_data.json
    if %ERRORLEVEL% NEQ 0 (
        color 0C
        echo [✗] ERROR: Dump failed.
        goto end
    )

    echo 📥 Reloading fixture directly...
    python manage.py loaddata core\fixtures\initial_data.json
    if %ERRORLEVEL% NEQ 0 (
        color 0C
        echo [✗] ERROR: Reload failed.
        goto end
    )

    :: Green for success
    color 0A
    echo ✅ Done! Database flushed, seeded, dumped, and reloaded successfully.
) else (
    color 0C
    echo [✗] Operation aborted.
)

:end
:: Reset to default
color 07
pause
