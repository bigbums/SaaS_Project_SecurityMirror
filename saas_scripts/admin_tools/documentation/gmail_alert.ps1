# gmail_alert.ps1
# Runs smoke_test.ps1, checks for errors, and sends an email alert via Gmail SMTP.

$smokeTestPath = "C:\Users\DELL\saas_scripts\admin_tools\smoke_test.ps1"
$output = & pwsh.exe -File $smokeTestPath
Write-Output $output

if ($output -match "

\[✗\]

") {
    $smtpServer = "smtp.gmail.com"
    $smtpPort   = 587
    $from       = "your_email@gmail.com"
    $to         = "recipient@example.com"

    $credential = Get-Credential  # Enter Gmail address + App Password

    $subject = "Smoke Test FAILED (Gmail)"
    $body    = "Errors detected in smoke test:`n`n$output"

    Send-MailMessage -SmtpServer $smtpServer -Port $smtpPort `
        -From $from -To $to -Subject $subject -Body $body `
        -Credential $credential -UseSsl
} else {
    Write-Output "Smoke test passed. No Gmail alert sent."
}
