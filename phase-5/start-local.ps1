# start-local.ps1
# This script automates port-forwarding for Phase 5 to resolve INVALID_ORIGIN issues.

# Self-elevate to Administrator if not already elevator
if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Start-Process powershell.exe "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

echo "Starting Phase 5 Local Port-Forwarding..."

# Kill any existing port-forwards on these ports
echo "Cleaning up existing port-forwards..."
Stop-Process -Name kubectl -ErrorAction SilentlyContinue

echo "Mapping Frontend to http://localhost:3000..."
Start-Process kubectl -ArgumentList "port-forward svc/todo-frontend 3000:80 --address 127.0.0.1" -NoNewWindow
Start-Sleep -Seconds 2

echo "Mapping API Gateway to http://localhost:8000..."
Start-Process kubectl -ArgumentList "port-forward svc/todo-backend 8000:8000 --address 127.0.0.1" -NoNewWindow
Start-Sleep -Seconds 2

echo "Phase 5 Services are now accessible:"
echo "-----------------------------------"
echo "Frontend: http://localhost:3000"
echo "API Gateway: http://localhost:8000"
echo "-----------------------------------"
echo "Press Ctrl+C to stop port-forwarding."

# Keep window open
while ($true) { Start-Sleep -Seconds 10 }
