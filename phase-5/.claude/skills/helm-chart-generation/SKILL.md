---
name: Helm Chart Generation
description: Helm expert for orchestrating cloud-native deployments for the todo-app.
---

# Helm Chart Generation

You are a Helm expert for cloud-native deployments.

- Generate a complete Helm chart under `charts/todo-app/` with:
  - `Chart.yaml` (name: `todo-app`, version: `0.1.0`)
  - `values.yaml` with configurable replicas, image tags, env vars (`DATABASE_URL`, `BETTER_AUTH_SECRET`, etc.)
  - `templates/` containing `Deployment.yaml`, `Service.yaml`, `Ingress.yaml` (optional for local)
  - Separate deployments for frontend and backend, plus Neon DB secret if needed.
- Use Kubernetes best practices: labels, resource limits, liveness/readiness probes.
- Enable Dapr annotations if preparing for Phase 5.
- Generate `helm install`/`upgrade` commands for Minikube testing.
- Reference: `@specs/deployment/helm.md`
