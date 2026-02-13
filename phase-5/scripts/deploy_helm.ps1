# Deploy Backend
Write-Host "Deploying Todo Backend..."
helm upgrade --install todo-backend ./charts/todo-backend `
  --set env.databaseUrl=$env:DATABASE_URL `
  --set env.openaiApiKey=$env:OPENAI_API_KEY `
  --set env.cerebrasApiKey=$env:CEREBRAS_API_KEY `
  --set env.betterAuthSecret=$env:BETTER_AUTH_SECRET

# Deploy Frontend
Write-Host "Deploying Todo Frontend..."
helm upgrade --install todo-frontend ./charts/todo-frontend `
  --set env.databaseUrl=$env:DATABASE_URL `
  --set env.betterAuthSecret=$env:BETTER_AUTH_SECRET `
  --set env.betterAuthUrl="http://localhost:3000" `
  --set env.nextPublicApiUrl="http://localhost:8000"

# Force a rollout restart to ensure pods pick up Secret changes
Write-Host "Restarting deployments to pick up latest secrets..."
kubectl rollout restart deployment todo-backend
kubectl rollout restart deployment todo-frontend

Write-Host "Deployment Complete!"
Write-Host "Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod --selector=app.kubernetes.io/name=todo-backend --timeout=90s
kubectl wait --for=condition=ready pod --selector=app.kubernetes.io/name=todo-frontend --timeout=90s

Write-Host "Services available:"
minikube service list
