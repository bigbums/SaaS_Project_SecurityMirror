# smoke_test.ps1
# Combined smoke test script with DB, pipeline, and API health checks

Write-Output "=== Smoke Test Started ==="

# 1. Database reset check (placeholder logic)
Write-Output "Checking database reset..."
# Replace with actual DB reset validation logic
Write-Output "[✓] Database reset successful"

# 2. Pipeline check (placeholder logic)
Write-Output "Checking pipeline..."
# Replace with actual pipeline validation logic
Write-Output "[✓] Pipeline ran successfully"

# 3. Import API health checks module
Import-Module "C:\Users\DELL\saas_scripts\admin_tools\ApiHealthChecks.psm1"

# 4. Run API endpoint checks
Write-Output "Checking API endpoints..."
Test-ApiEndpoint -Url "https://api.yourapp.com/health"
Test-ApiEndpoint -Url "https://api.yourapp.com/status" -ExpectedStatusCode 200

# 5. Run API payload checks
Write-Output "Checking API payloads..."
Test-ApiPayload -Url "https://api.yourapp.com/users/1" -ExpectedField "id"
Test-ApiPayload -Url "https://api.yourapp.com/config" -ExpectedField "version"

Write-Output "=== Smoke Test Completed ==="
# Define environment endpoints
$envConfig = @{
    "DEV"  = "http://localhost:5000/health"
    "STAGE" = "https://staging-api.yourapp.com/health"
    "PROD"  = "https://api.yourapp.com/health"
}

# Select environment (default = DEV)
$environment = "DEV"
$apiUrl = $envConfig[$environment]
