# Implementation Plan: Intermediate & Advanced Todo Chatbot Features

**Branch**: `1-todo-chatbot-features` | **Date**: 2024-10-27 | **Spec**: specs/1-todo-chatbot-features/spec.md
**Input**: Feature specification from specs/1-todo-chatbot-features/spec.md

## Summary

This plan outlines the implementation of Intermediate (Priorities, Tags/Categories, Search & Filter, Sort) and Advanced (Recurring Tasks, Due Dates & Reminders with notifications) features for the Todo Chatbot. It involves an event-driven architecture using Kafka and full Dapr integration, with deployment targeting Minikube and cloud Kubernetes. The implementation will leverage specific Phase 5 skills for microservices development, event stream processing, actions scheduling, and Kubernetes orchestration.

## Technical Context

**Language/Version**: Python 3.11+ (FastAPI for microservices)
**Primary Dependencies**: FastAPI, Dapr SDK (Python), Kafka client library (e.g., confluent-kafka-python or similar), SQLModel, PostgreSQL client (asyncpg)
**Storage**: PostgreSQL (used via Dapr State Management component, likely Neon Serverless)
**Testing**: pytest
**Target Platform**: Kubernetes (Minikube for local, DigitalOcean DOKS for cloud)
**Project Type**: Microservices (backend services)
**Performance Goals**: Sub-second response times for typical task operations; scalable event processing.
**Constraints**: Resource limits (CPU < 700m, memory < 1Gi per pod); adherence to Dapr best practices; event-driven patterns.
**Scale/Scope**: Supports individual user task management, scaling to handle a moderate number of users and their tasks.
**Structure Decision**: Single project with multiple microservices; each service managed as a distinct deployable unit within the Kubernetes cluster.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Phase 5 Constitution v2.0.0+**

- [x] **Skill-Driven Development**: Does the plan explicitly map implementation tasks to the required Phase 5 skills (e.g., `event-driven-architect`, `kafka-stream-processing`, etc.)?
- [x] **Full Dapr Integration**: Does the architecture plan utilize Dapr for its core components (Pub/Sub, State, Bindings, Secrets, Service Invocation)?
- [x] **Event-Driven Architecture**: Is Kafka (or a compatible system like Redpanda) integrated for the event-driven backbone?
- [x] **Staged Deployment**: Does the plan include distinct stages for Minikube and cloud Kubernetes deployment?
- [x] **Resource Management**: Are resource limits (CPU < 700m, Memory < 1Gi) and probes defined for all services?
- [x] **Traceability**: Is there a clear link between proposed changes, tasks, and the skills used?

## Project Structure

### Documentation (this feature)

```text
specs/1-todo-chatbot-features/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Multi-service backend structure (implied by FastAPI microservices)
src/
├── api_gateway/        # FastAPI service for external requests, NL processing
├── notification_service/ # FastAPI service for sending reminders/notifications
├── recurring_task_service/ # FastAPI service for managing recurring tasks
├── task_service/       # Existing/extended FastAPI service for core task management
├── shared/             # Common models, utilities, Dapr client
└── tests/              # Combined tests for all services (unit, integration)

deploy/                 # Helm charts, Dapr components, K8s manifests
```

**Structure Decision**: A multi-service backend structure is adopted to accommodate the new microservices and Dapr integration, with shared components and a dedicated deployment directory.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Multi-service architecture | Required for Dapr integration and modularity/scalability of new features | Monolithic API would become unmanageable with event-driven patterns and specialized services (notifications, recurring tasks). |
| Event-driven patterns | Decoupling services for scalability and resilience | Direct service-to-service calls would introduce tight coupling, reduce fault tolerance, and complicate integration of Kafka/Dapr. |
