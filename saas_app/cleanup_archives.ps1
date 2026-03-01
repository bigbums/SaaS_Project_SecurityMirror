# cleanup_archives.ps1
$settings = Get-Content "settings.json" | ConvertFrom-Json
$retention = $settings.log_retention_days

$old = Get-ChildItem "reports\archives" -Filter "*.zip" | Where-Object {
    $_.LastWriteTime -lt (Get-Date).AddDays(-$retention)
}

if ($old.Count -gt 0) {
    $old | Remove-Item -Force
    Add-Content "run_logs_and_health.log" ("Deleted " + $old.Count + " old archives older than " + $retention + " days at " + (Get-Date))
} else {
    Add-Content "run_logs_and_health.log" ("No archives older than " + $retention + " days found at " + (Get-Date))
}
