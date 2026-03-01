# Extended Smoke Test for menu.ps1
# Path to your menu.ps1 script
$scriptPath = "C:\Users\DELL\saas_scripts\admin_tools\menu.ps1"

# Define the test cases
$tests = @(
    @{ Choice = "1"; Description = "Reset DB" },
    @{ Choice = "2"; Description = "Seed DB" },
    @{ Choice = "7"; Description = "Full Automated Test" },
    @{ Choice = "X"; Description = "Pipeline Reset→Seed→Full Test" },
    @{ Choice = "8"; Description = "View Current Log" },
    @{ Choice = "9"; Description = "Clear Current Log" },
    @{ Choice = "A"; Description = "View All Logs" },
    @{ Choice = "D"; Description = "Delete Old Logs" },
    @{ Choice = "Z"; Description = "Invalid Option" }
)

Write-Host "============================================" -ForegroundColor Yellow
Write-Host "   Running Extended Smoke Test for menu.ps1" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Yellow

foreach ($test in $tests) {
    Write-Host "`n[>] Testing option $($test.Choice): $($test.Description)" -ForegroundColor Green
    try {
        pwsh.exe -File $scriptPath $($test.Choice)
        Write-Host "[✓] Test completed for $($test.Description)" -ForegroundColor Cyan
    }
    catch {
        Write-Host "[✗] Error running $($test.Description): $_" -ForegroundColor Red
    }
}

Write-Host "`nExtended smoke test finished. Check automation logs for details." -ForegroundColor Yellow
