# Robust Deployment Script (Safe from Shell Escaping)

# 1. Validate required environment variables
$requiredVars = @("DATABASE_URL", "BETTER_AUTH_SECRET", "OPENAI_API_KEY", "CEREBRAS_API_KEY")
foreach ($var in $requiredVars) {
    $val = [System.Environment]::GetEnvironmentVariable($var, "Process")
    if ([string]::IsNullOrWhiteSpace($val)) {
        Write-Error "CRITICAL: environment variable `$env:$var is NOT set. Deployment aborted."
        exit 1
    }
}

Write-Host "All environment variables verified. Encoding secrets..." -ForegroundColor Green

# 2. Create a temporary secrets file
$secretsYaml = @"
env:
  databaseUrl: "$($env:DATABASE_URL)"
  betterAuthSecret: "$($env:BETTER_AUTH_SECRET)"
  openaiApiKey: "$($env:OPENAI_API_KEY)"
  cerebrasApiKey: "$($env:CEREBRAS_API_KEY)"
"@

$secretsPath = Join-Path $PSScriptRoot "temp-secrets.yaml"
$secretsYaml | Out-File -FilePath $secretsPath -Encoding utf8

try {
    # 3. Deploy Backend
    Write-Host "Deploying Todo Backend (Securely)..." -ForegroundColor Cyan
    helm upgrade --install todo-backend ./charts/todo-backend -f $secretsPath

    # 4. Deploy Frontend
    Write-Host "Deploying Todo Frontend (Securely)..." -ForegroundColor Cyan
    helm upgrade --install todo-frontend ./charts/todo-frontend -f $secretsPath `
      --set env.nextPublicApiUrl="http://localhost:8000"

    Write-Host "`nDeployment Triggered Successfully! 🚀" -ForegroundColor Green
    Write-Host "Waiting for pods to rotate..."
    kubectl rollout status deployment/todo-frontend --timeout=60s
    kubectl rollout status deployment/todo-backend --timeout=60s

} finally {
    # 5. Cleanup sensitive file
    if (Test-Path $secretsPath) { Remove-Item $secretsPath }
}

Write-Host "`nServices available:"
minikube service list
