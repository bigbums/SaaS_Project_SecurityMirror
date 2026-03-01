. "C:\users\dell\saas_scripts\admin_tools\config.ps1"

# Define log file path
$logFile = "C:\users\dell\saas_scripts\admin_tools\automation.log"

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

do {
    Clear-Host
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    Write-Output "============================================"
    Write-Output "   SaaS Automation Menu (with Logging)"
    Write-Output "   Session started at: $timestamp"
    Write-Output "============================================"

    Write-Output "1. Reset DB"
    Write-Output "2. Seed DB"
    Write-Output "3. Dump DB"
    Write-Output "4. Load DB"
    Write-Output "5. Reset + Seed"
    Write-Output "6. Reset + Dump + Seed"
    Write-Output "7. Run Full Automated Test"
    Write-Output "8. View Logs"
    Write-Output "9. Clear Logs"
    Write-Output "H. Help/About"
    Write-Output "0. Exit"

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

            # Calculate summary
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
            Write-Output "`n[>] Displaying automation.log..."
            Get-Content $logFile | Out-Host
            Pause
        }
        "9" {
            Write-Output "`n[>] Clearing automation.log..."
            Clear-Content $logFile
            Write-Output "[✓] Log file cleared."
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
            Write-Output "7. Run Full Test   - Executes all scripts sequentially with logging"
            Write-Output "8. View Logs       - Displays automation.log contents"
            Write-Output "9. Clear Logs      - Clears automation.log file"
            Write-Output "H. Help/About      - Shows this guide"
            Write-Output "0. Exit            - Quits the menu"
            Write-Output "============================================"
            Pause
        }
        "0" { Write-Output "Exiting..."; break }
        default { Write-Output "Invalid choice. Please try again."; Pause }
    }
} while ($choice -ne "0")
