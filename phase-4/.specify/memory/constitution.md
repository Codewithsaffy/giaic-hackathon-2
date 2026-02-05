<!-- SYNC IMPACT REPORT
Version change: 1.3.0 → 1.4.0
Modified principles: Kubernetes Deployment Constitution updated to explicitly reference Phase 4 skills and deployment requirements
Added sections: None
Removed sections: None
Templates requiring updates: .specify/templates/plan-template.md, .specify/templates/spec-template.md, .specify/templates/tasks-template.md ✅ updated for consistency
Follow-up TODOs: None
-->

# Kubernetes Deployment Constitution

## System Constraints

1. This deployment EXTENDS the existing Phase 3 Todo Chatbot application.
2. Existing authentication, UI, REST APIs, and database models MUST NOT be modified during deployment.
3. All containerization, Helm charting, and deployment MUST be performed by invoking the specific Phase 4 skills defined in SKILL.md.
4. Explicitly use "Docker Containerization" skill for Dockerfiles and Gordon integration.
5. Explicitly use "Helm Chart Generation" skill for Chart.yaml, values.yaml, and templates.
6. Explicitly use "Minikube Local Deployment Orchestration" skill for deployment sequence and AIOps commands.
7. Explicitly use "Infrastructure Spec Validation" skill before finalizing any implementation.
8. Explicitly use "Blueprint Creation" skill for bonus reusable artifacts.
9. Never write Docker/Helm/K8s configs without referencing the relevant skill.
10. Skills are the single source of truth for patterns and best practices.
11. Resource limits: CPU < 500m, memory < 512Mi. Readiness/liveness probes required.
12. Prepare Dapr annotations for Phase 5.
13. All code/config must trace to tasks and skills.
14. No manual coding — implementation via Claude Code only.

## Core Invariants

### I. Skill-First Approach
All containerization, Helm charting, and deployment operations must be performed through the designated Phase 4 skills. Direct manual configuration of Dockerfiles, Helm charts, or Kubernetes manifests is prohibited without explicit skill invocation.

### II. Claude Code Only
No manual coding is performed outside Claude Code. All code generation, modification, and management is performed through Claude Code tools and processes.

### III. Spec-Kit Plus Workflow
All development follows the Spec-Kit Plus workflow. Every feature must be specified, planned, and task-broken down before implementation begins.

## Reusable Intelligence Policy

### I. Preferred Over Reimplementation
Reusable intelligence should be preferred over re-deriving solutions. When existing patterns, components, or solutions exist, they should be leveraged rather than recreated to maintain consistency and reduce redundancy.

### II. Project-Local Skills Priority
Project-local skills take priority over plugin or user skills. When a skill clearly matches a task's intent, it should be used. If a skill is not applicable, the reason should be implicit in the output.

### III. Skill Intent Matching
Skills are applied only when they match the task intent. The appropriateness of skill usage should be evaluated based on the specific requirements and context of each task.

## Architectural Invariants

### I. Containerization Requirements
Docker containerization must be performed using the "Docker Containerization" skill with Gordon integration. All container images must be optimized for production deployment with minimal attack surface and proper security configurations.

### II. Helm Chart Requirements
Helm charts must be generated using the "Helm Chart Generation" skill with properly configured Chart.yaml, values.yaml, and Kubernetes template files. Charts must support configurable resource limits and service discovery.

### III. Minikube Deployment Orchestration
Deployment to local Kubernetes must be orchestrated using the "Minikube Local Deployment Orchestration" skill with appropriate AIOps commands. Deployment sequences must include proper service startup ordering and health checks.

### IV. Resource Constraints Enforcement
Kubernetes resources must enforce strict CPU and memory limits: CPU < 500m, memory < 512Mi. All deployments must include readiness and liveness probes to ensure service availability and proper restart behavior.

### V. Dapr Preparation for Phase 5
All Kubernetes deployments must prepare for Dapr integration by including appropriate annotations and service configurations. This includes sidecar injection readiness and distributed tracing configuration points.

## Security Invariants

### I. Infrastructure Spec Validation
All infrastructure implementations must pass validation through the "Infrastructure Spec Validation" skill before deployment. Security best practices, resource compliance, and architectural alignment must be verified.

### II. API Authentication Requirement
All API endpoints require authentication. Requests without valid credentials must return HTTP 401 status code, ensuring that no unauthenticated access is permitted.

### III. Data Access Isolation
Users may only access their own data. Strong data isolation is enforced at both the application and database levels to prevent cross-user data access.

### IV. Credential Validation
All requests must include valid authentication credentials. Invalid or missing credentials result in access denial with appropriate error responses.

## Governance

All development activities must comply with this constitution. Changes to these principles require explicit documentation and approval. The constitution serves as the authoritative guide for development decisions and architectural choices. All containerization, Helm charting, and deployment operations must utilize the designated Phase 4 skills rather than direct configuration.

**Version**: 1.4.0 | **Ratified**: 2026-01-06 | **Last Amended**: 2026-02-04