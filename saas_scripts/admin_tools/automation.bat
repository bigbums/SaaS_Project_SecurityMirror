@echo off
:: ==============================
:: Batch Automation Scripts
:: ==============================

:: Color scheme legend:
::   Green  = Success
::   Yellow = Warning / Confirmation
::   Red    = Error / Abort

:: Reset script (dangerous!)
:reset
color 0E
echo WARNING: This will RESET the database and DELETE all data!
set /p confirm="Are you sure you want to continue? (Y/N): "
if /I "%confirm%"=="Y" (
    color 0C
    echo Resetting database...
    python manage.py reset_db --noinput
    color 0A
    echo Database reset complete.
) else (
    color 0C
    echo Reset aborted.
)
goto end

:: Seed script
:seed
color 0E
echo Seeding database with initial data...
python manage.py loaddata seed_data.json
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo ERROR: Seeding failed.
) else (
    color 0A
    echo Seeding complete.
)
goto end

:: Dump script
:dump
color 0E
echo Dumping database to JSON...
python manage.py dumpdata > dump.json
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo ERROR: Dump failed.
) else (
    color 0A
    echo Dump complete.
)
goto end

:: Load script
:load
color 0E
echo Loading database from dump.json...
python manage.py loaddata dump.json
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo ERROR: Load failed.
) else (
    color 0A
    echo Load complete.
)
goto end

:end
color 07
echo Done.
pause
