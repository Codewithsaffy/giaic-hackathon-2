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

2.  **Install Dapr CLI and Initialize Dapr**:
    ```bash
    dapr init -k
    ```
    This command initializes Dapr on your local Kubernetes cluster (Minikube).

3.  **Configure Dapr Components**:
    Apply the necessary Dapr component configurations (e.g., Kafka Pub/Sub, PostgreSQL State Store) to your Kubernetes cluster. These will typically be in `deploy/dapr-components/`.
    ```bash
    kubectl apply -f deploy/dapr-components/
    ```

4.  **Deploy Microservices with Helm**:
    Use the extended Helm chart to deploy all microservices to Minikube.
    ```bash
    helm upgrade --install todo-chatbot-features ./deploy/helm/todo-chatbot-features -f ./deploy/helm/todo-chatbot-features/values-minikube.yaml
    ```

5.  **Verify Deployment**:
    Check if all pods are running and Dapr sidecars are injected:
    ```bash
    kubectl get pods -l app.kubernetes.io/instance=todo-chatbot-features
    dapr list
    ```

6.  **Access Chatbot (TBD)**:
    Instructions on how to access the chatbot interface and interact with the new features will be provided upon full implementation.

## Interacting with New Features (Conceptual)

Once deployed, you would interact with the chatbot using natural language commands to:
-   Set task priorities (e.g., "Set priority of 'buy groceries' to high")
-   Add tags to tasks (e.g., "Add tags 'urgent', 'personal' to 'call mom'")
-   Search/filter tasks (e.g., "Show me high priority tasks with tag 'work'")
-   Create recurring tasks (e.g., "Create a task 'daily standup' every weekday at 9 AM")
-   Set due dates and reminders (e.g., "Set 'project report' due for tomorrow 5 PM, remind me 1 hour before")

## Cleanup

To remove the deployment from Minikube:
```bash
helm uninstall todo-chatbot-features
dapr uninstall --kubernetes
```

This guide is preliminary and will be refined with concrete commands and access points during development.
