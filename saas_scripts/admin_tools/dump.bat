@echo off
cd /d C:\Users\DELL\saas_app

:: Cyan for action
color 0B
echo [>] Dumping database to JSON...
python manage.py dumpdata > dump.json

:: Success check
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo [✗] ERROR: Dump failed.
) else (
    color 0A
    echo [✓] Database dumped successfully to dump.json!
)

:: Reset to default
color 07
pause
