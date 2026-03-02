[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 -bor [Net.SecurityProtocolType]::Tls13

function Test-ApiPerformance {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory=$true)]
        [string]$Url,
        [int]$ThresholdMs = 2000
    )

    try {
        $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

        $null = Invoke-WebRequest -Uri $Url -TimeoutSec 10 -ErrorAction Stop
        $stopwatch.Stop()

        $elapsed = $stopwatch.ElapsedMilliseconds
        if ($elapsed -le $ThresholdMs) {
            Write-Output "[OK] $Url responded in $elapsed ms (within threshold)"
        } else {
            Write-Output "[FAIL] $Url responded in $elapsed ms (exceeds $ThresholdMs ms threshold)"
        }
    }
    catch {
        Write-Output ("[FAIL] $Url performance check failed: {0}" -f $_.Exception.Message)
    }
}

function Test-ApiSslCertificate {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory=$true)]
        [string]$Url
    )

    try {
        $uri = [System.Uri]$Url
        $tcpClient = New-Object System.Net.Sockets.TcpClient($uri.Host, 443)
        $sslStream = New-Object System.Net.Security.SslStream($tcpClient.GetStream(), $false, { return $true })
        $sslStream.AuthenticateAsClient($uri.Host)

        $cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2($sslStream.RemoteCertificate)
        $expiry = $cert.NotAfter
        $now = Get-Date

        if ($expiry -gt $now) {
            Write-Output "[OK] SSL certificate for $Url is valid until $expiry"
        } else {
            Write-Output "[FAIL] SSL certificate for $Url expired on $expiry"
        }

        $sslStream.Close()
        $tcpClient.Close()
    }
    catch {
        Write-Output ("[FAIL] SSL certificate check failed for {0}: {1}" -f $Url, $_.Exception.Message)
    }
}
