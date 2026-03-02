param(
    [switch]$Uninstall,
    [switch]$Test,
    [switch]$ExportSummary,
    [int]$RetentionDays = 30   # Default retention period is 30 days
)

# Base directory (dynamic: folder where this script lives)
$baseDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

# Default values (can be overridden by config file)
[string]$logFile       = Join-Path $baseDir "setup_log.txt"
[string]$iconsDir      = Join-Path $baseDir "icons"
[string]$reportsDir    = Join-Path $baseDir "reports"
[int]$scheduledHour    = 8   # default run time is 8 AM

# --- Load config file if present ---
$configFile = Join-Path $baseDir "healthcheck_config.json"
if (Test-Path $configFile) {
    try {
        $config = Get-Content $configFile | ConvertFrom-Json

        if ($config.RetentionDays) {
            $RetentionDays = [int]$config.RetentionDays
        }
        if ($config.LogFileName) {
            $logFile = Join-Path $baseDir $config.LogFileName
        }
        if ($config.IconsFolder) {
            $iconsDir = Join-Path $baseDir $config.IconsFolder
        }
        if ($config.ReportsFolder) {
            $reportsDir = Join-Path $baseDir $config.ReportsFolder
        }
        if ($config.ScheduledHour) {
            $scheduledHour = [int]$config.ScheduledHour
        }
    } catch {
        Write-Host "⚠️ Could not read config file: $($_.Exception.Message)"
    }
}


# Timestamped summary filename
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$summaryFile = "$baseDir\summary_report_$timestamp.txt"

# Track results
$results = @{}


function Write-Log {
    param([string]$Message)
    $timestampLog = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $entry = "[$timestampLog] $Message"
    Add-Content -Path $logFile -Value $entry
    Write-Host $Message
}

function Show-ErrorToast {
    param([string]$Message)
    Import-Module BurntToast -ErrorAction SilentlyContinue
    $errorIcon = "$baseDir\icons\error.png"
    New-BurntToastNotification -Text "❌ HealthCheck Error", $Message -AppLogo $errorIcon
}

function Invoke-Retry {
    param(
        [scriptblock]$Action,
        [string]$Description,
        [string]$Key
    )
    try {
        & $Action
        Write-Log "✅ $Description succeeded."
        $results[$Key] = "Success"
    } catch {
        Write-Log "⚠️ $Description failed: $($_.Exception.Message). Retrying..."
        try {
            & $Action
            Write-Log "✅ $Description succeeded on retry."
            $results[$Key] = "Success (after retry)"
        } catch {
            Write-Log "❌ $Description failed after retry: $($_.Exception.Message)"
            Show-ErrorToast "$Description failed after retry: $($_.Exception.Message)"
            $results[$Key] = "Failed"
        }
    }
}

function Show-Summary {
    Write-Host "`n================ SUMMARY CHECKLIST ================" -ForegroundColor Cyan
    $summaryOutput = @()
    $failedSteps = 0

    foreach ($step in $results.Keys) {
        switch -Regex ($results[$step]) {
            "Success" { 
                Write-Host ("{0}: ✅ {1}" -f $step, $results[$step]) -ForegroundColor Green
                $summaryOutput += ("{0}: ✅ {1}" -f $step, $results[$step])
            }
            "Success \(after retry\)" { 
                Write-Host ("{0}: ⚠️ {1}" -f $step, $results[$step]) -ForegroundColor Yellow
                $summaryOutput += ("{0}: ⚠️ {1}" -f $step, $results[$step])
            }
            "Failed" { 
                Write-Host ("{0}: ❌ {1}" -f $step, $results[$step]) -ForegroundColor Red
                $summaryOutput += ("{0}: ❌ {1}" -f $step, $results[$step])
                $failedSteps++
            }
            default { 
                Write-Host ("{0}: {1}" -f $step, $results[$step]) -ForegroundColor White
                $summaryOutput += ("{0}: {1}" -f $step, $results[$step])
            }
        }
    }

    Write-Host "===================================================" -ForegroundColor Cyan

    if ($ExportSummary) {
        $summaryOutput | Out-File $summaryFile -Encoding UTF8
        Add-Content -Path $summaryFile -Value "Generated at: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
        Write-Log "📄 Summary exported to $summaryFile"
    }

    # Final toast popup
    Import-Module BurntToast -ErrorAction SilentlyContinue
    if ($failedSteps -eq 0) {
        New-BurntToastNotification -Text "✅ HealthCheck Summary", "All steps succeeded." -AppLogo (Join-Path $iconsDir "success.png")
    } else {
        New-BurntToastNotification -Text "❌ HealthCheck Summary", "Some steps failed — check $summaryFile" -AppLogo (Join-Path $iconsDir "error.png")
    }
}

# --- Cleanup old summary files based on retention period ---
$summaryDir = $baseDir
Get-ChildItem -Path $summaryDir -Filter "summary_report_*.txt" -ErrorAction SilentlyContinue |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-$RetentionDays) } |
    ForEach-Object {
        try {
            Remove-Item $_.FullName -Force
            Write-Log "🧹 Deleted old summary file: $($_.Name)"
        } catch {
            Write-Log "⚠️ Could not delete old summary file: $($_.Name) - $($_.Exception.Message)"
        }
    }

# --- Uninstall Mode ---
if ($Uninstall) {
    Write-Log "Starting HealthCheck uninstall..."

    Invoke-Retry { 
        if (Get-ScheduledTask -TaskName "HealthCheck Daily" -ErrorAction SilentlyContinue) {
            Unregister-ScheduledTask -TaskName "HealthCheck Daily" -Confirm:$false
        }
    } "Remove Task Scheduler job" "Task Scheduler"

    Invoke-Retry { Remove-EventLog -Source "HealthCheckScript" } "Remove Event Log source" "Event Log"

    Invoke-Retry { 
        if (Get-Module -ListAvailable -Name BurntToast) {
            Uninstall-Module -Name BurntToast -Force
        }
    } "Uninstall BurntToast module" "BurntToast"

    Write-Log "✅ HealthCheck uninstall complete."
    Show-Summary
    exit
}

# --- Test Mode ---
if ($Test) {
    Write-Log "Starting HealthCheck self-test..."

    Invoke-Retry { 
        Write-EventLog -LogName Application -Source "HealthCheckScript" -EntryType Information -EventId 9999 -Message "HealthCheck self-test event"
    } "Write test entry to Event Viewer" "Event Log Test"

    Invoke-Retry { 
        Import-Module BurntToast
        New-BurntToastNotification -Text "🔔 HealthCheck Self-Test", "Toast notifications are working." -AppLogo "$baseDir\icons\success.png"
    } "Display test toast notification" "Toast Test"

    Write-Log "✅ HealthCheck self-test complete."
    Show-Summary
    exit
}

# --- Normal Install Path ---
Write-Log "Starting HealthCheck setup..."

Invoke-Retry { 
    if (-not (Test-Path "$baseDir\reports")) { New-Item -ItemType Directory -Path "$baseDir\reports" | Out-Null }
    if (-not (Test-Path "$baseDir\icons"))   { New-Item -ItemType Directory -Path "$baseDir\icons" | Out-Null }
} "Verify folder structure" "Folders"

Invoke-Retry { 
    if (-not (Get-Module -ListAvailable -Name BurntToast)) {
        Install-Module -Name BurntToast -Force
    }
    Import-Module BurntToast
} "Install and import BurntToast" "BurntToast"

Invoke-Retry { 
    if (-not (Get-EventLog -LogName Application -Source "HealthCheckScript" -ErrorAction SilentlyContinue)) {
        New-EventLog -LogName Application -Source "HealthCheckScript"
    }
} "Register Event Log source" "Event Log"

Invoke-Retry {
    $action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$baseDir\run_logs_and_health.bat`""

    # Trigger at the configured hour (default 8 AM, or from config file)
    $trigger = New-ScheduledTaskTrigger -Daily -At (Get-Date "00:00").AddHours($scheduledHour)

    # Explicitly set principal to your current user with highest privileges
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest

    $task = New-ScheduledTask -Action $action -Trigger $trigger -Principal $principal -Description "Runs health_check.py daily and generates summary"

    try {
        Register-ScheduledTask -TaskName "HealthCheck Daily" -InputObject $task -Force -User $env:USERNAME
    } catch {
        throw "Failed to register scheduled task: $($_.Exception.Message)"
    }
} "Create Task Scheduler job" "Task Scheduler"

Write-Log "✅ Setup complete! HealthCheck will now run daily at $scheduledHour:00."

# --- Run Self-Test Automatically After Install ---
Invoke-Retry { 
    Write-EventLog -LogName Application -Source "HealthCheckScript" -EntryType Information -EventId 9999 -Message "HealthCheck install self-test event"
    New-BurntToastNotification -Text "🔔 HealthCheck Install Test", "Setup complete and notifications working." -AppLogo "$baseDir\icons\success.png"
} "Run automatic self-test after installation" "Self-Test"

Show-Summary
