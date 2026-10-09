# FlowCare AI — PowerShell Live Endpoint Status Verifier (Checks HTTP 200 OK)
# Run this while uvicorn is running on http://127.0.0.1:8000

$baseUrl = "http://127.0.0.1:8000"

$endpoints = @(
    "/health",
    "/",
    "/data-quality",
    "/data/overview",
    "/data/patients",
    "/data/appointments",
    "/data/beds",
    "/data/staff",
    "/data/diagnostics",
    "/data/admissions",
    "/data/discharges",
    "/data/feedback",
    "/dashboard",
    "/bottlenecks",
    "/causal-links",
    "/recommendations",
    "/priority-queue",
    "/actions",
    "/audit-log"
)

Write-Host "==========================================================================" -ForegroundColor Cyan
Write-Host " FlowCare AI — Live HTTP 200 OK Verifier (http://127.0.0.1:8000)" -ForegroundColor Cyan
Write-Host "==========================================================================" -ForegroundColor Cyan
Write-Host ("{0,-38} | {1,-10} | {2,-8}" -f "ENDPOINT", "STATUS", "RESULT")
Write-Host "--------------------------------------------------------------------------"

$passed = 0
$failed = 0

foreach ($ep in $endpoints) {
    $url = "$baseUrl$ep"
    try {
        $response = Invoke-WebRequest -Uri $url -Method Get -UseBasicParsing -TimeoutSec 5
        $code = $response.StatusCode
        if ($code -eq 200) {
            Write-Host ("{0,-38} | {1,-10} | [PASS]" -f $ep, $code) -ForegroundColor Green
            $passed++
        } else {
            Write-Host ("{0,-38} | {1,-10} | [FAIL]" -f $ep, $code) -ForegroundColor Red
            $failed++
        }
    } catch {
        Write-Host ("{0,-38} | {1,-10} | [FAIL - $($_.Exception.Message)]" -f $ep, "ERROR") -ForegroundColor Red
        $failed++
    }
}

Write-Host "--------------------------------------------------------------------------"
Write-Host "TOTAL CHECKED: $($passed + $failed) | PASSED: $passed | FAILED: $failed"
Write-Host "==========================================================================" -ForegroundColor Cyan

if ($failed -eq 0) {
    Write-Host ">>> ALL LIVE ENDPOINTS RETURNED 200 OK! <<<" -ForegroundColor Green
} else {
    Write-Host ">>> SOME ENDPOINTS FAILED. ENSURE UVICORN IS RUNNING ON PORT 8000! <<<" -ForegroundColor Yellow
}
