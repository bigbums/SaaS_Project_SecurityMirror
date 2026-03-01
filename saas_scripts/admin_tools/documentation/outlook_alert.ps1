# outlook_alert.ps1
# Runs smoke_test.ps1, checks for errors, and sends an email alert via Outlook SMTP.

$smokeTestPath = "C:\Users\DELL\saas_scripts\admin_tools\smoke_test.ps1"
$output = & pwsh.exe -File $smokeTestPath
Write-Output $output

if ($output -match "

\[✗\]

") {
    $smtpServer = "smtp.office365.com"
    $smtpPort   = 587
    $from       = "your_email@outlook.com"
    $to         = "recipient@example.com"

    $credential = Get-Credential  # Enter Outlook/Office365 credentials

    $subject = "Smoke Test FAILED (Outlook)"
    $body    = "Errors detected in smoke test:`n`n$output"

    Send-MailMessage -SmtpServer $smtpServer -Port $smtpPort `
        -From $from -To $to -Subject $subject -Body $body `
        -Credential $credential -UseSsl
} else {
    Write-Output "Smoke test passed. No Outlook alert sent."
}
