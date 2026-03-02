# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

# Load config.ps1 from the same directory
. "$ScriptDir\config.ps1"

# Define log file path with timestamp
$sessionTimestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$logFile = Join-Path $ScriptDir "automation_$sessionTimestamp.log"

# Capture command-line argument (if provided)
param(
    [string]$AutoChoice
)

function RunBatch {
    param([string]$scriptPath, [string]$label)

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Output ""
    Write-Output "[>] Running $label..."
    Add-Content -Path $logFile -Value "$timestamp [>] Running $label..."

    Start-Process "cmd.exe" "/c $scriptPath" -Wait
    if ($LASTEXITCODE -eq 0) {
        Write-Output "[✓] $label completed successfully."
        Add-Content -Path $logFile -Value "$timestamp [✓] $label completed successfully."
        return "Success"
    } else {
        Write-Output "[✗] $label failed with exit code $LASTEXITCODE."
        Add-Content -Path $logFile -Value "$timestamp [✗] $label failed with exit code $LASTEXITCODE."
        return "Failed"
    }
}

# --- Auto-run mode (for Task Scheduler) ---
# --- Auto-run mode (for Task Scheduler) ---
if ($AutoChoice) {
    Write-Output "[>] Auto-running option $AutoChoice..."
    switch ($AutoChoice) {
        "1" { RunBatch $Scripts["ResetDB"] "Reset DB" }
        "2" { RunBatch $Scripts["SeedDB"] "Seed DB" }
        "3" { RunBatch $Scripts["DumpDB"] "Dump DB" }
        "4" { RunBatch $Scripts["LoadDB"] "Load DB" }
        "5" { RunBatch $Scripts["ResetSeed"] "Reset + Seed" }
        "6" { RunBatch $Scripts["ResetAndSeed"] "Reset + Dump + Seed" }
        "7" {
            Write-Output "`n[>] Running Full Automated Test..."
            $results = @()
            $results += @{Label="Reset DB";       Status=(RunBatch $Scripts["ResetDB"] "Reset DB")}
            $results += @{Label="Seed DB";        Status=(RunBatch $Scripts["SeedDB"] "Seed DB")}
            $results += @{Label="Dump DB";        Status=(RunBatch $Scripts["DumpDB"] "Dump DB")}
            $results += @{Label="Load DB";        Status=(RunBatch $Scripts["LoadDB"] "Load DB")}
            $results += @{Label="Reset + Seed";   Status=(RunBatch $Scripts["ResetSeed"] "Reset + Seed")}
            $results += @{Label="Reset + Dump + Seed"; Status=(RunBatch $Scripts["ResetAndSeed"] "Reset + Dump + Seed")}

            $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            $total   = $results.Count
            $success = ($results | Where-Object { $_.Status -eq "Success" }).Count
            $failed  = ($results | Where-Object { $_.Status -eq "Failed" }).Count
            $failedNames = ($results | Where-Object { $_.Status -eq "Failed" }).Label -join ", "

            if ($failed -gt 0) {
                $summary = "$timestamp Summary: $total scripts run, $success succeeded, $failed failed (Failed: $failedNames)"
            } else {
                $summary = "$timestamp Summary: $total scripts run, $success succeeded, $failed failed"
            }

            Write-Output $summary
            Add-Content -Path $logFile -Value $summary
        }
        "8" {
            Write-Output "`n[>] Displaying current log file..."
            Get-Content $logFile | Out-Host
        }
        "9" {
            Write-Output "`n[>] Clearing current log file..."
            Clear-Content $logFile
            Write-Output "[✓] Current log file cleared."
        }
        "A" {
            Write-Output "`n[>] Listing all log files..."
            $logs = Get-ChildItem -Path $ScriptDir -Filter "automation_*.log" | Sort-Object LastWriteTime -Descending
            if ($logs.Count -eq 0) {
                Write-Output "No log files found."
            } else {
                $i = 1
                foreach ($log in $logs) {
                    Write-Output "[$i] $($log.Name) (Last modified: $($log.LastWriteTime))"
                    $i++
                }
            }
        }
        "D" {
            Write-Output "`n[>] Deleting old logs (keeping last 5)..."
            $logs = Get-ChildItem -Path $ScriptDir -Filter "automation_*.log" | Sort-Object LastWriteTime -Descending
            if ($logs.Count -gt 5) {
                $oldLogs = $logs | Select-Object -Skip 5
                foreach ($log in $oldLogs) {
                    Remove-Item $log.FullName -Force
                    Write-Output "[✓] Deleted $($log.Name)"
                }
            } else {
                Write-Output "No old logs to delete (less than or equal to 5 logs exist)."
            }
        }
        default {
            Write-Output "Auto-choice $AutoChoice not implemented for automation."
        }
    }
    exit
}


# --- Interactive menu mode ---
do {
    Clear-Host
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    Write-Host "============================================" -ForegroundColor Yellow
    Write-Host "   SaaS Automation Menu (Portable Edition)" -ForegroundColor Cyan
    Write-Host "   Session started at: $timestamp" -ForegroundColor DarkGray
    Write-Host "   Current log file: $logFile" -ForegroundColor DarkGray
    Write-Host "============================================" -ForegroundColor Yellow

    Write-Host "[1] Reset DB"
    Write-Host "[2] Seed DB"
    Write-Host "[3] Dump DB"
    Write-Host "[4] Load DB"
    Write-Host "[5] Reset + Seed"
    Write-Host "[6] Reset + Dump + Seed"
    Write-Host "[7] Run Full Automated Test (with summary)"
    Write-Host "[8] View Current Log"
    Write-Host "[9] Clear Current Log"
    Write-Host "[A] View All Logs"
    Write-Host "[D] Delete Old Logs (keep last 5)"
    Write-Host "[H] Help/About"
    Write-Host "[0] Exit"
    Write-Host "============================================" -ForegroundColor Yellow

    $choice = Read-Host "Select an option"

    switch ($choice) {
        "1" { RunBatch $Scripts["ResetDB"] "Reset DB"; Pause }
        "2" { RunBatch $Scripts["SeedDB"] "Seed DB"; Pause }
        "3" { RunBatch $Scripts["DumpDB"] "Dump DB"; Pause }
        "4" { RunBatch $Scripts["LoadDB"] "Load DB"; Pause }
        "5" { RunBatch $Scripts["ResetSeed"] "Reset + Seed"; Pause }
        "6" { RunBatch $Scripts["ResetAndSeed"] "Reset + Dump + Seed"; Pause }
        "7" {
            Write-Output "`n[>] Running Full Automated Test..."
            $results = @()
            $results += @{Label="Reset DB";       Status=(RunBatch $Scripts["ResetDB"] "Reset DB")}
            $results += @{Label="Seed DB";        Status=(RunBatch $Scripts["SeedDB"] "Seed DB")}
            $results += @{Label="Dump DB";        Status=(RunBatch $Scripts["DumpDB"] "Dump DB")}
            $results += @{Label="Load DB";        Status=(RunBatch $Scripts["LoadDB"] "Load DB")}
            $results += @{Label="Reset + Seed";   Status=(RunBatch $Scripts["ResetSeed"] "Reset + Seed")}
            $results += @{Label="Reset + Dump + Seed"; Status=(RunBatch $Scripts["ResetAndSeed"] "Reset + Dump + Seed")}

            $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            $total   = $results.Count
            $success = ($results | Where-Object { $_.Status -eq "Success" }).Count
            $failed  = ($results | Where-Object { $_.Status -eq "Failed" }).Count
            $failedNames = ($results | Where-Object { $_.Status -eq "Failed" }).Label -join ", "

            if ($failed -gt 0) {
                $summary = "$timestamp Summary: $total scripts run, $success succeeded, $failed failed (Failed: $failedNames)"
            } else {
                $summary = "$timestamp Summary: $total scripts run, $success succeeded, $failed failed"
            }

            Write-Output $summary
            Add-Content -Path $logFile -Value $summary
            Pause
        }
        "8" {
            Write-Output "`n[>] Displaying current log file..."
            Get-Content $logFile | Out-Host
            Pause
        }
        "9" {
            Write-Output "`n[>] Clearing current log file..."
            Clear-Content $logFile
            Write-Output "[✓] Current log file cleared."
            Pause
        }
        "A" {
            Write-Output "`n[>] Listing all log files..."
            $logs = Get-ChildItem -Path $ScriptDir -Filter "automation_*.log" | Sort-Object LastWriteTime -Descending
            if ($logs.Count -eq 0) {
                Write-Output "No log files found."
            } else {
                $i = 1
                foreach ($log in $logs) {
                    Write-Output "[$i] $($log.Name) (Last modified: $($log.LastWriteTime))"
                    $i++
                }
                $selection = Read-Host "Enter the number of the log file to view"
                if ($selection -match '^\d+$' -and [int]$selection -le $logs.Count) {
                    $chosenLog = $logs[[int]$selection - 1].FullName
                    Write-Output "`n[>] Displaying $chosenLog..."
                    Get-Content $chosenLog | Out-Host
                } else {
                    Write-Output "Invalid selection."
                }
            }
            Pause
        }
        "D" {
            Write-Output "`n[>] Deleting old logs (keeping last 5)..."
            $logs = Get-ChildItem -Path $ScriptDir -Filter "automation_*.log" | Sort-Object LastWriteTime -Descending
            if ($logs.Count -gt 5) {
                $oldLogs = $logs | Select-Object -Skip 5
                foreach ($log in $oldLogs) {
                    Remove-Item $log.FullName -Force
                    Write-Output "[✓] Deleted $($log.Name)"
                }
            } else {
                Write-Output "No old logs to delete (less than or equal to 5 logs exist)."
            }
            Pause
        }
        "H" {

            Write-Output "`n============================================"
            Write-Output "   Help / About"
            Write-Output "============================================"
            Write-Output "1. Reset DB        - Clears database to a fresh state"
            Write-Output "2. Seed DB         - Populates database with sample data"
            Write-Output "3. Dump DB         - Exports current database contents"
            Write-Output "4. Load DB         - Imports database from dump file"
            Write-Output "5. Reset + Seed    - Resets and then seeds database"
            Write-Output "6. Reset + Dump + Seed - Full cycle: reset, dump, seed"
            Write-Output "7. Run Full Test   - Executes all scripts sequentially with logging + summary"
            Write-Output "8. View Current Log - Displays current session log file"
            Write-Output "9. Clear Current Log - Clears current session log file"
            Write-Output "A. View All Logs   - Lists all log files and lets you view one"
            Write-Output "D. Delete Old Logs - Deletes older logs, keeping only the last 5"
            Write-Output "H. Help/About      - Shows this guide"
            Write-Output "0. Exit            - Quits the menu"
            Write-Output "============================================"
            Pause
        }
        "0" { Write-Host "Exiting menu..." -ForegroundColor Red; break }
        default { Write-Host "Invalid choice. Please try again." -ForegroundColor Red; Pause }
    }
} while ($choice -ne "0")

