# Quickstart: Intermediate & Advanced Todo Chatbot Features

This document provides a high-level quickstart guide for setting up and running the Intermediate and Advanced features of the Todo Chatbot. More detailed instructions will be provided during the implementation phase.

## Prerequisites

-   Docker Desktop (with Kubernetes enabled for Minikube simulation)
-   `kubectl` (Kubernetes command-line tool)
-   `helm` (Kubernetes package manager)
-   `dapr` CLI (Distributed Application Runtime command-line interface)
-   Python 3.11+
-   `pip` (Python package installer)

## Setup and Deployment (Local Minikube)

1.  **Clone the Repository**:
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **Initialize Minikube Environment**:
    ```powershell
    minikube start
    minikube docker-env | Invoke-Expression
    ```

3.  **Build Service Images**:
    ```bash
    docker build -t backend:phase5 ./backend
    docker build -t frontend:phase5 ./frontend --build-arg NEXT_PUBLIC_API_URL=http://localhost:8000
    # Build supporting microservices using the shared Dockerfile
    docker build -t notification-service:phase5 -f src/shared/Dockerfile.microservice --build-arg SERVICE_NAME=notification_service .
    ```

4.  **Configure Dapr Components**:
    Apply the Redis infrastructure and Dapr component configurations.
    ```bash
    kubectl apply -f deploy/redis.yaml
    kubectl apply -f deploy/dapr-components/
    ```

5.  **Deploy Application Services**:
    Apply the Kubernetes manifests for all services.
    ```bash
    kubectl apply -f deploy/
    ```

6.  **Verify Deployment**:
    Check if all pods are running and Dapr components are active:
    ```bash
    kubectl get pods
    dapr list -k
    ```

7.  **Access Chatbot**:
    Use the provided script to automate port-forwarding:
    ```powershell
    ./start-local.ps1
    ```
    - **Frontend**: http://localhost:3000
    - **API**: http://localhost:8000/docs

## Interacting with New Features

Once deployed, you can interact with the chatbot to:
-   **Priorities**: "Set priority of 'buy groceries' to 1"
-   **Tags**: "Add tags 'urgent' to 'call mom'"
-   **Reminders**: "Remind me tomorrow at 5 PM about 'meeting'"
-   **Recurring**: "Set task 'daily report' to recur daily"

## Cleanup

To remove the deployment from Minikube:
```bash
helm uninstall todo-chatbot-features
dapr uninstall --kubernetes
```

This guide is preliminary and will be refined with concrete commands and access points during development.
