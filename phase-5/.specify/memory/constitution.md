<!-- SYNC IMPACT REPORT
Version change: 1.4.0 → 2.0.0
Modified principles: Complete overhaul for Phase 5, replacing Kubernetes Deployment constitution with Event-Driven Microservices constitution.
Added sections: All sections redefined to align with Phase 5 goals.
Removed sections: All Phase 4 sections removed.
Templates requiring updates: .specify/templates/plan-template.md ✅ updated for consistency
Follow-up TODOs: None
-->

# Todo Chatbot Phase 5 Constitution

## Goal

Implement all Intermediate (Priorities, Tags/Categories, Search & Filter, Sort) and Advanced (Recurring Tasks, Due Dates & Time Reminders) features in the Todo Chatbot, integrate event-driven architecture with Kafka and full Dapr, and deploy to Minikube then cloud Kubernetes (DigitalOcean DOKS preferred).

## Core Principles

### 1. Skill-Driven Development
**Principle**: All implementation MUST explicitly invoke the relevant Phase 5 skills as defined in `SKILL.md` (e.g., `event-driven-architect`, `kafka-stream-processing`, `fastapi-microservices-development`, `kubernetes`).
**Rationale**: To ensure adherence to specified architectural patterns, leverage expert-defined workflows, and maintain consistency across the project.

### 2. Full Dapr Integration
**Principle**: The system MUST use Dapr for its core distributed application capabilities, including Pub/Sub (with a Kafka component), State Management (with PostgreSQL/Neon), Bindings (for cron jobs/reminders), Secrets, and Service-to-Service Invocation.
**Rationale**: To build a resilient, portable, and decoupled microservices architecture that abstracts away underlying infrastructure complexities.

### 3. Event-Driven Architecture with Kafka
**Principle**: The architecture MUST be event-driven, using Kafka (or a compatible alternative like Redpanda) as the event streaming backbone. Key topics will include `task-events`, `reminders`, and `task-updates`.
**Rationale**: To decouple microservices, enable asynchronous communication, and improve scalability and fault tolerance.

### 4. Staged Deployment Strategy
**Principle**: All new features and services MUST be deployed first to a local Minikube environment for validation before being promoted to a cloud-based Kubernetes cluster (DigitalOcean DOKS is preferred).
**Rationale**: To validate deployment manifests, service interactions, and overall functionality in a controlled environment, reducing the risk of production failures.

### 5. Strict Resource Management
**Principle**: All containerized services MUST define and respect resource limits: CPU under 700m and memory under 1Gi per pod. All pods MUST have readiness and liveness probes configured.
**Rationale**: To ensure application stability, prevent resource starvation, enable effective auto-scaling, and maintain a cost-effective operational footprint.

### 6. Absolute Traceability of Changes
**Principle**: All code and configuration changes MUST trace back to a specific, defined task and MUST explicitly reference the skill(s) used for the implementation.
**Rationale**: To maintain a clear audit trail, enforce accountability, and ensure every change aligns with a planned unit of work and follows established patterns.

### 7. CI/CD Readiness
**Principle**: All development work should prepare for and facilitate future automation. This includes creating CI/CD hints and designing components that are easily testable and deployable, with a preference for GitHub Actions pipelines.
**Rationale**: To streamline the path to production, reduce manual deployment errors, and enable a rapid, reliable release cadence.

## Governance

All development activities must comply with this constitution. Changes to these principles require explicit documentation and approval.

**Version**: 2.0.0 | **Ratified**: 2024-10-27 | **Last Amended**: 2024-10-27
