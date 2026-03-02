# email_alert.ps1
# Runs smoke_test.ps1, checks for errors, and sends an email alert if any are found.

# Path to your smoke test script
$smokeTestPath = "C:\Users\DELL\saas_scripts\admin_tools\smoke_test.ps1"

# Run the smoke test and capture output
$output = & pwsh.exe -File $smokeTestPath
Write-Output $output

# Check for error markers in output
if ($output -match "

\[✗\]

") {
    # Email settings (configure these!)
    $smtpServer = "smtp.yourmailserver.com"
    $smtpPort   = 587
    $from       = "alerts@yourdomain.com"
    $to         = "bunmi@yourdomain.com"

    # Use Get-Credential to securely store credentials
    $credential = Get-Credential

    $subject = "Smoke Test FAILED"
    $body    = "The smoke test detected errors. Output:`n`n$output"

    Send-MailMessage -SmtpServer $smtpServer -Port $smtpPort `
        -From $from -To $to -Subject $subject -Body $body `
        -Credential $credential -UseSsl
} else {
    Write-Output "Smoke test passed. No email alert sent."
}
