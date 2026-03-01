@echo off
cd /d C:\Users\DELL\saas_app

:: Cyan for action
color 0B
echo [>] Loading database from dump.json...
python manage.py loaddata dump.json

:: Success check
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo [✗] ERROR: Load failed.
) else (
    color 0A
    echo [✓] Database loaded successfully from dump.json!
)

:: Reset to default
color 07
pause
