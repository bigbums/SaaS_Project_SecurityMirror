@echo off
cd /d C:\Users\DELL\saas_app

:: Yellow for warning
color 0E
echo [!] WARNING: This will FLUSH the database (delete all data but keep schema/migrations).
set /p confirm="Are you sure you want to continue? (Y/N): "

if /I "%confirm%"=="Y" (
    :: Cyan for action
    color 0B
    echo [>] Flushing database...
    python manage.py flush --no-input

    :: Check for static folder
    if not exist "C:\Users\DELL\saas_app\static" (
        color 0E
        echo [!] Warning: static folder not found at C:\Users\DELL\saas_app\static
    )

    :: Success check
    if %ERRORLEVEL% NEQ 0 (
        color 0C
        echo [✗] ERROR: Flush failed.
    ) else (
        color 0A
        echo [✓] Database flushed successfully!
    )
) else (
    color 0C
    echo [✗] Operation aborted.
)

:: Reset to default
color 07
pause
