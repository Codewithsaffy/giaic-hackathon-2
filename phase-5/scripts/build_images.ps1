# Enable Minikube's Docker daemon
Write-Host "Setting up Minikube Docker environment..."
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

# Build Backend
Write-Host "Building Backend Image (todo-backend)..."
docker build -t todo-backend:latest ./backend

# Build Frontend
Write-Host "Building Frontend Image (todo-frontend)..."
docker build -t todo-frontend:latest ./frontend

Write-Host "Build Complete!"
docker images | findstr todo
