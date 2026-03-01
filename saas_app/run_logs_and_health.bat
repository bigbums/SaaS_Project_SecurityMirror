@echo off
cd C:\Users\DELL\Saas_Project\saas_app

REM Activate the virtual environment
call ..\.venv\Scripts\activate.bat

REM Ensure archive folder exists
if not exist reports\archives (
    mkdir reports\archives
)

REM Archive previous log with date stamp if it exists
set LOGFILE=run_logs_and_health.log
set ARCHIVE=reports\archives\run_logs_and_health_%date:~-4%%date:~4,2%%date:~7,2%.log
set ZIPARCHIVE=reports\archives\run_logs_and_health_%date:~-4%%date:~4,2%%date:~7,2%.zip

if exist %LOGFILE% (
    copy %LOGFILE% %ARCHIVE%
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Compress-Archive -Path '%ARCHIVE%' -DestinationPath '%ZIPARCHIVE%' -Force"
    del %ARCHIVE%
    del %LOGFILE%
)

REM Cleanup: run PowerShell script for archive retention
powershell -NoProfile -ExecutionPolicy Bypass -File cleanup_archives.ps1


REM Add timestamp before running convert_logs.py
echo ==== Starting convert_logs.py at %date% %time% ==== >> %LOGFILE%
python convert_logs.py >> %LOGFILE% 2>&1

REM Add timestamp before running health_check.py
echo ==== Starting health_check.py at %date% %time% ==== >> %LOGFILE%
python health_check.py all >> %LOGFILE% 2>&1

REM Add final timestamp after completion
echo ==== Workflow completed at %date% %time% ==== >> %LOGFILE%

REM Send email notification with log attached
REM powershell -NoProfile -ExecutionPolicy Bypass -Command ^
REM "$smtpServer = 'smtp.yourmailserver.com'; `
REM   $from = 'alerts@yourdomain.com'; `
REM   $to = 'bunmi.sadiq@gmail.com'; `
REM   $subject = 'Workflow Completed'; `
REM   $body = 'The scheduled workflow has finished. See attached log.'; `
REM   $attachment = 'run_logs_and_health.log'; `
REM   Send-MailMessage -SmtpServer $smtpServer -From $from -To $to -Subject $subject -Body $body -Attachments $attachment"

REM Send email notification with log attached
REM powershell -NoProfile -ExecutionPolicy Bypass -File send_email.ps1 -LogFile run_logs_and_health.log

REM Email notification disabled for now
REM powershell -NoProfile -ExecutionPolicy Bypass -File send_email.ps1 -LogFile run_logs_and_health.log

REM Generate daily summary report
powershell -NoProfile -ExecutionPolicy Bypass -File generate_summary.ps1
