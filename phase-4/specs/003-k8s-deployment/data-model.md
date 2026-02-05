# Data Model: Containerize and Deploy Todo Chatbot to Minikube

## Overview
The deployment configuration for the Todo Chatbot on Kubernetes involves several configuration artifacts and data structures that define how the application is packaged, deployed, and managed in the Kubernetes environment. This model includes containerization specifications, Helm chart structures, and Kubernetes resource definitions.

## Container Image Specifications

### Frontend Container (Next.js)
- **Image Name**: `todo-frontend`
- **Base Image**: `node:18-alpine` (production), `node:18` (development)
- **Build Stages**:
  - Build Stage: Install dependencies, run build process
  - Runtime Stage: Copy built assets, run production server
- **Exposed Port**: 3000
- **Environment Variables**:
  - `NODE_ENV`: Set to "production" in built image
  - `NEXT_PUBLIC_API_URL`: URL of backend service
  - `PORT`: Port to listen on (default: 3000)
- **Security Context**: Non-root user (UID 1001)
- **Health Checks**: Built-in Next.js health endpoints

### Backend Container (FastAPI)
- **Image Name**: `todo-backend`
- **Base Image**: `python:3.11-slim`
- **Build Stages**:
  - Build Stage: Install Python dependencies, compile extensions
  - Runtime Stage: Copy application code, run server
- **Exposed Port**: 8000
- **Environment Variables**:
  - `ENVIRONMENT`: Set to "production" in deployed environment
  - `DATABASE_URL`: Connection string for PostgreSQL database
  - `AUTH_SECRET`: JWT secret for authentication
  - `PORT`: Port to listen on (default: 8000)
- **Security Context**: Non-root user (UID 1001)
- **Health Checks**: `/health` endpoint returning service status

## Kubernetes Resources Configuration

### Deployment Specifications
- **Frontend Deployment**:
  - Name: `todo-frontend`
  - Replicas: Configurable (default: 1)
  - Image: `todo-frontend:<tag>`
  - Ports: 3000 (HTTP)
  - Resource Requests: CPU 100m, Memory 128Mi
  - Resource Limits: CPU 400m, Memory 384Mi (within <500m CPU, <512Mi memory requirement)
  - Environment Variables: NEXT_PUBLIC_API_URL, NODE_ENV
  - Readiness Probe: HTTP GET on `/api/health`
  - Liveness Probe: HTTP GET on `/api/health`
  - Annotations: Dapr sidecar configuration for Phase 5 preparation
  - Labels: `app=todo-frontend`, `version=latest`

- **Backend Deployment**:
  - Name: `todo-backend`
  - Replicas: Configurable (default: 1)
  - Image: `todo-backend:<tag>`
  - Ports: 8000 (HTTP)
  - Resource Requests: CPU 100m, Memory 128Mi
  - Resource Limits: CPU 400m, Memory 384Mi (within <500m CPU, <512Mi memory requirement)
  - Environment Variables: DATABASE_URL, AUTH_SECRET, ENVIRONMENT
  - Readiness Probe: HTTP GET on `/health`
  - Liveness Probe: HTTP GET on `/health`
  - Annotations: Dapr sidecar configuration for Phase 5 preparation
  - Labels: `app=todo-backend`, `version=latest`

### Service Specifications
- **Frontend Service**:
  - Name: `todo-frontend-service`
  - Type: ClusterIP (internal), NodePort (external access via Minikube)
  - Port: 80 -> 3000 (targetPort)
  - Selector: `app=todo-frontend`
  - Labels: `app=todo-frontend`, `service=frontend`

- **Backend Service**:
  - Name: `todo-backend-service`
  - Type: ClusterIP
  - Port: 80 -> 8000 (targetPort)
  - Selector: `app=todo-backend`
  - Labels: `app=todo-backend`, `service=backend`

### ConfigMap Structure
- **Frontend ConfigMap**:
  - Name: `todo-frontend-config`
  - Labels: `app=todo-frontend`
  - Keys:
    - `NEXT_PUBLIC_API_URL`: URL of the backend service in format `http://todo-backend-service:80`
    - `NODE_ENV`: Node environment setting

- **Backend ConfigMap**:
  - Name: `todo-backend-config`
  - Labels: `app=todo-backend`
  - Keys:
    - `LOG_LEVEL`: Application logging level (default: INFO)
    - `ENVIRONMENT`: Environment name (default: production)

### Secret Structure
- **Application Secrets**:
  - Name: `todo-app-secrets`
  - Type: Opaque
  - Keys:
    - `auth-secret`: Authentication secret for JWT signing
    - `database-password`: Password for database connection (mounted from external secret)

## Helm Chart Data Model

### Chart Metadata (Chart.yaml)
- **Name**: `todo-chatbot`
- **Version**: `0.1.0`
- **AppVersion**: Matches application version
- **Description**: Helm chart for Todo Chatbot deployment
- **Home**: Link to application documentation
- **Maintainers**: List of maintainers
- **Icon**: URL to application icon

### Value Structure (values.yaml)
- **Global Values**:
  - `global.imageRegistry`: Container registry for all images
  - `global.storageClass`: Storage class for persistent volumes (if needed)
  - `global.rbac.create`: Whether to create RBAC resources

- **Frontend Configuration Values**:
  - `frontend.enabled`: Whether to deploy frontend (default: true)
  - `frontend.image.repository`: Frontend image repository
  - `frontend.image.tag`: Frontend image tag (default: "latest")
  - `frontend.image.pullPolicy`: Image pull policy (default: IfNotPresent)
  - `frontend.service.type`: Service type (default: ClusterIP)
  - `frontend.service.port`: Service port (default: 80)
  - `frontend.service.targetPort`: Target port (default: 3000)
  - `frontend.resources.limits.cpu`: CPU limit (default: 400m)
  - `frontend.resources.limits.memory`: Memory limit (default: 384Mi)
  - `frontend.resources.requests.cpu`: CPU request (default: 100m)
  - `frontend.resources.requests.memory`: Memory request (default: 128Mi)
  - `frontend.replicaCount`: Number of replicas (default: 1)
  - `frontend.nodeSelector`: Node selection constraints
  - `frontend.tolerations`: Taint tolerations
  - `frontend.affinity`: Pod affinity/anti-affinity rules

- **Backend Configuration Values**:
  - `backend.enabled`: Whether to deploy backend (default: true)
  - `backend.image.repository`: Backend image repository
  - `backend.image.tag`: Backend image tag (default: "latest")
  - `backend.image.pullPolicy`: Image pull policy (default: IfNotPresent)
  - `backend.service.type`: Service type (default: ClusterIP)
  - `backend.service.port`: Service port (default: 80)
  - `backend.service.targetPort`: Target port (default: 8000)
  - `backend.resources.limits.cpu`: CPU limit (default: 400m)
  - `backend.resources.limits.memory`: Memory limit (default: 384Mi)
  - `backend.resources.requests.cpu`: CPU request (default: 100m)
  - `backend.resources.requests.memory`: Memory request (default: 128Mi)
  - `backend.replicaCount`: Number of replicas (default: 1)
  - `backend.env.databaseUrl`: Database connection URL
  - `backend.env.authSecret`: Authentication secret
  - `backend.nodeSelector`: Node selection constraints
  - `backend.tolerations`: Taint tolerations
  - `backend.affinity`: Pod affinity/anti-affinity rules

- **Dapr Configuration Values**:
  - `dapr.enabled`: Enable Dapr sidecar injection (default: false)
  - `dapr.appId`: Dapr application ID (default: todo-app)
  - `dapr.config`: Dapr configuration name (default: "")
  - `dapr.enableHttps`: Enable HTTPS for Dapr (default: false)

- **Infrastructure Validation Values**:
  - `validation.enabled`: Enable infrastructure validation (default: true)
  - `validation.policy`: Policy to enforce (default: standard)

## API Contract Specifications

### Frontend API Endpoints
- **GET /**: Main application page
- **GET /api/health**: Health check endpoint
- **POST /api/chat**: Natural language command processing
- **GET /api/todos**: Retrieve todo list
- **POST /api/todos**: Create new todo item
- **PUT /api/todos/:id**: Update todo item
- **DELETE /api/todos/:id**: Delete todo item

### Backend API Endpoints
- **GET /health**: Health check endpoint
- **GET /todos**: Retrieve todo list
- **POST /todos**: Create new todo item
- **PUT /todos/:id**: Update todo item
- **DELETE /todos/:id**: Delete todo item
- **POST /chat**: Natural language processing endpoint
- **GET /docs**: Interactive API documentation
- **GET /redoc**: Alternative API documentation

## Deployment Configuration Model

### Environment Configuration
- **Development Environment**:
  - Resource requests: Lower limits for local development
  - Log levels: Verbose for debugging
  - Security: Reduced for development convenience

- **Production Environment**:
  - Resource limits: Strict adherence to <500m CPU, <512Mi memory
  - Log levels: Standard production levels
  - Security: Full security configurations applied

### Networking Model
- **Internal Communication**: Service-to-service communication using Kubernetes DNS
- **External Access**: NodePort service for Minikube access
- **Load Balancing**: Kubernetes service load balancing
- **Traffic Routing**: Round-robin distribution among pods

### Security Model
- **Authentication**: JWT-based authentication inherited from Phase 3
- **Authorization**: Role-based access control
- **Network Security**: Default deny policy with explicit allow rules
- **Pod Security**: Non-root execution, read-only root filesystem where possible