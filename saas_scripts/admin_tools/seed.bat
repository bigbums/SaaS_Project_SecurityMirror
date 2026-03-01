@echo off
cd /d C:\Users\DELL\saas_app

:: Cyan for action
color 0B
echo [>] Seeding database with initial data...
python manage.py loaddata seed_data.json

:: Success check
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo [✗] ERROR: Seeding failed.
) else (
    color 0A
    echo [✓] Database seeded successfully!
)

:: Reset to default
color 07
pause
