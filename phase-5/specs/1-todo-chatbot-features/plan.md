# Implementation Plan: Intermediate & Advanced Todo Chatbot Features

**Branch**: `1-todo-chatbot-features` | **Date**: 2024-10-27 | **Spec**: specs/1-todo-chatbot-features/spec.md
**Input**: Feature specification from specs/1-todo-chatbot-features/spec.md

## Summary

This plan outlines the implementation of Intermediate (Priorities, Tags, Search & Filter, Sort) and Advanced (Recurring Tasks, Due Dates & Reminders) features for the Todo Chatbot. It involves an event-driven architecture using Redis and full Dapr integration, with deployment targeting Minikube. The implementation leverages SpecitPlus and Claude Code workflows for a spec-first approach.

## Technical Context

**Language/Version**: Python 3.11+ (FastAPI for microservices)
**Primary Dependencies**: FastAPI, Dapr SDK (Python), Redis, SQLModel, PostgreSQL client (asyncpg)
**Storage**: Redis (used for Pub/Sub and State), PostgreSQL (Neon) for task persistence.
**Testing**: pytest
**Target Platform**: Kubernetes (Minikube local setup)
**Project Type**: Microservices (distributed backend)
**Performance Goals**: Sub-second response times; scalable event processing via Redis topics.
**Constraints**: Resource limits (CPU < 500m, memory < 512Mi per pod); adherence to Dapr best practices.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Phase 5 Constitution v2.0.0+**

- [x] **Skill-Driven Development**: Does the plan explicitly map implementation tasks to the required Phase 5 skills?
- [x] **Full Dapr Integration**: Does the architecture plan utilize Dapr for core components (Pub/Sub, State, Bindings, Service Invocation)?
- [x] **Event-Driven Architecture**: Is Redis integrated for the event-driven backbone?
- [x] **Staged Deployment**: Does the plan include distinct stages for local Minikube deployment?
- [x] **Resource Management**: Are resource limits and probes defined for all services?
- [x] **Traceability**: Is there a clear link between proposed changes, tasks, and the skills used?

## Project Structure

### Documentation (this feature)

```text
specs/1-todo-chatbot-features/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan
├── data-model.md        # Data model definitions
├── quickstart.md        # Feature quickstart
└── tasks.md             # Actionable roadmap
```

### Source Code (repository root)

```text
src/
├── notification_service/ # Handles reminders/notifications via Dapr Jobs API
├── recurring_task_service/ # Manages recurring task logic
├── audit_service/        # Logs all system events for traceability
└── shared/               # Common models and microservice base logic

backend/                  # Core task management service
deploy/                   # Kubernetes manifests and Dapr components
```
deploy/                 # Helm charts, Dapr components, K8s manifests
```

**Structure Decision**: A multi-service backend structure is adopted to accommodate the new microservices and Dapr integration, with shared components and a dedicated deployment directory.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Multi-service architecture | Required for Dapr integration and modularity/scalability of new features | Monolithic API would become unmanageable with event-driven patterns and specialized services (notifications, recurring tasks). |
| Event-driven patterns | Decoupling services for scalability and resilience | Direct service-to-service calls would introduce tight coupling, reduce fault tolerance, and complicate integration of Kafka/Dapr. |
