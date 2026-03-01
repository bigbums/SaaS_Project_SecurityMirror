if (-not (Get-Module -ListAvailable -Name BurntToast)) {
    Install-Module -Name BurntToast -Force
}
Import-Module BurntToast



# --- Generate Daily Summary Report ---

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# Health status
if (Test-Path "reports\health_status.txt") {
    $health = Get-Content "reports\health_status.txt"
} else {
    $health = @("No health status file found. (Default: System OK)")
}

# Error count
if (Test-Path "reports\error_log.txt") {
    $errors = Get-Content "reports\error_log.txt"
    $errorCount = ($errors | Measure-Object).Count
} else {
    $errorCount = 0
}

# Cleanup result
$cleanupResult = "Cleanup completed successfully."

# --- Format Summary ---
$summary = @"
================ DAILY SUMMARY ================
Run at: $timestamp

--- Health Status ---
$(($health -join "`n"))

--- Error Log ---
Total errors in error_log.txt: $errorCount

--- Cleanup ---
$cleanupResult
===============================================
"@

# Write to file
$summary | Out-File "reports\daily_summary.txt" -Encoding UTF8

# --- Console Output with Colors + Sounds + Event Logs ---
Write-Host "================ DAILY SUMMARY ================" -ForegroundColor Cyan
Write-Host "Run at: $timestamp" -ForegroundColor White

Write-Host "`n--- Health Status ---" -ForegroundColor Cyan
foreach ($line in $health) {
    if ($line -like "*✅*") {
        Write-Host $line -ForegroundColor Green
        [console]::beep(1000, 200)
        Write-EventLog -LogName Application -Source "HealthCheckScript" -EntryType Information -EventId 1000 -Message $line
    } elseif ($line -like "*⚠️*") {
        Write-Host $line -ForegroundColor Yellow
        [console]::beep(600, 400)
        Write-EventLog -LogName Application -Source "HealthCheckScript" -EntryType Warning -EventId 1001 -Message $line
    } elseif ($line -like "*❌*") {
        Write-Host $line -ForegroundColor Red
        [console]::beep(300, 800)
        Write-EventLog -LogName Application -Source "HealthCheckScript" -EntryType Error -EventId 1002 -Message $line
    } else {
        Write-Host $line -ForegroundColor White
    }
}

Write-Host "`n--- Error Log ---" -ForegroundColor Cyan
if ($errorCount -eq 0) {
    Write-Host "Total errors in error_log.txt: $errorCount" -ForegroundColor Green
    Write-EventLog -LogName Application -Source "HealthCheckScript" -EntryType Information -EventId 1003 -Message "No errors found in error_log.txt"
} else {
    Write-Host "Total errors in error_log.txt: $errorCount" -ForegroundColor Red
    [console]::beep(250, 1000)
    Write-EventLog -LogName Application -Source "HealthCheckScript" -EntryType Error -EventId 1004 -Message "Errors found in error_log.txt: $errorCount"
}

Write-Host "`n--- Cleanup ---" -ForegroundColor Cyan
Write-Host $cleanupResult -ForegroundColor Green
[console]::beep(1200, 200)
Write-EventLog -LogName Application -Source "HealthCheckScript" -EntryType Information -EventId 1005 -Message $cleanupResult

Write-Host "===============================================" -ForegroundColor Cyan

# --- Toast Notifications with Icons ---
Import-Module BurntToast

# Paths to icons (make sure these files exist)
$successIcon = "C:\Users\DELL\Saas_Project\icons\success.png"
$warningIcon = "C:\Users\DELL\Saas_Project\icons\warning.png"
$errorIcon   = "C:\Users\DELL\Saas_Project\icons\error.png"

# Success toast if no errors
if ($errorCount -eq 0) {
    New-BurntToastNotification -Text "✅ Health Check Success", "No errors detected." -AppLogo $successIcon
}
# Error toast if errors exist
elseif ($errorCount -gt 0) {
    New-BurntToastNotification -Text "❌ Health Check Alert", "Errors detected in logs ($errorCount). Check daily_summary.txt." -AppLogo $errorIcon
}

# Warning toast for any ⚠️ lines in health_status
foreach ($line in $health) {
    if ($line -like "*⚠️*") {
        New-BurntToastNotification -Text "⚠️ Health Check Warning", $line -AppLogo $warningIcon
    }
}
