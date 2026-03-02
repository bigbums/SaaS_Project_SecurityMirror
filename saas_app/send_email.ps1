# send_email.ps1
param(
    [string]$LogFile = "run_logs_and_health.log"
)

$smtpServer = "smtp.gmail.com"   # or smtp.gmail.com
$smtpPort   = 587
$from       = "your_email@domain.com"
$to         = "your_email@domain.com"
$subject    = "Workflow Completed"
$body       = "The scheduled workflow has finished. See attached log."

# Secure password prompt (store once in Windows Credential Manager for safety)
$credential = Get-Credential

Send-MailMessage -SmtpServer $smtpServer -Port $smtpPort -UseSsl `
    -Credential $credential -From $from -To $to `
    -Subject $subject -Body $body -Attachments $LogFile
