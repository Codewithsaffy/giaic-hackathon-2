Write-Host "=== Starting Port Forwarding ===" -ForegroundColor Cyan
Write-Host "Opening separate windows for port-forwarding..."

Write-Host "Checking services..." -ForegroundColor Yellow
$services = kubectl get services -o json | ConvertFrom-Json
$backendExists = $services.items | Where-Object { $_.metadata.name -eq "todo-backend" }
$frontendExists = $services.items | Where-Object { $_.metadata.name -eq "todo-frontend" }

if (-not $backendExists) {
    Write-Error "Backend service not found!"
    exit 1
}
if (-not $frontendExists) {
    Write-Error "Frontend service not found!"
    exit 1
}

Write-Host "Services found" -ForegroundColor Green

Write-Host "Cleaning up old port-forwards..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -eq "kubectl"} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Write-Host "Starting Backend port-forward..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "kubectl port-forward service/todo-backend 8000:8000"
Start-Sleep -Seconds 3

Write-Host "Starting Frontend port-forward..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "kubectl port-forward service/todo-frontend 3000:80"
Start-Sleep -Seconds 3

Write-Host "Testing connectivity..." -ForegroundColor Yellow
$backendTest = Test-NetConnection -ComputerName 127.0.0.1 -Port 8000 -WarningAction SilentlyContinue
$frontendTest = Test-NetConnection -ComputerName 127.0.0.1 -Port 3000 -WarningAction SilentlyContinue

if ($backendTest.TcpTestSucceeded) {
    Write-Host "Backend OK at http://localhost:8000" -ForegroundColor Green
} else {
    Write-Host "Backend NOT accessible" -ForegroundColor Red
}

if ($frontendTest.TcpTestSucceeded) {
    Write-Host "Frontend OK at http://localhost:3000" -ForegroundColor Green
} else {
    Write-Host "Frontend NOT accessible" -ForegroundColor Red
}

Write-Host "`n=== Port Forwarding Active ===" -ForegroundColor Green
Write-Host "Access http://localhost:3000"
Write-Host "Close the new windows to stop forwarding"
