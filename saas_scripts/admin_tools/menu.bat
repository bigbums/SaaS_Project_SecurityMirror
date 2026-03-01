@echo off
cd /d C:\Users\DELL\saas_app

:menu
color 0E
echo ============================================
echo   SaaS Automation Menu
echo ============================================
echo [1] Reset DB (flush only)
echo [2] Seed DB
echo [3] Dump DB
echo [4] Load DB
echo [5] Reset + Seed
echo [6] Reset + Dump + Seed
echo [7] Exit
echo ============================================
set /p choice="Select an option (1-7): "

if "%choice%"=="1" (
    call resetdb.bat
    goto menu
)
if "%choice%"=="2" (
    call seed.bat
    goto menu
)
if "%choice%"=="3" (
    call dump.bat
    goto menu
)
if "%choice%"=="4" (
    call load.bat
    goto menu
)
if "%choice%"=="5" (
    call reset_seed.bat
    goto menu
)
if "%choice%"=="6" (
    call reset_and_seed.bat
    goto menu
)
if "%choice%"=="7" (
    goto end
)

echo [!] Invalid choice. Please try again.
goto menu

:end
color 07
echo Exiting menu...
pause
