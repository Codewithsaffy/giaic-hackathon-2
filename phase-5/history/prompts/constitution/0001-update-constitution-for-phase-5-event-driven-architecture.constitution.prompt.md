---
id: 0001
title: Update Constitution for Phase 5 Event-Driven Architecture
stage: constitution
date: 2024-10-27
surface: agent
model: gemini-1.5-flash
feature: none
branch: main
user: user
command: /sp.constitution Implement all Intermediate (Priorities, Tags/Categories, Search & Filter, Sort) and Advanced (Recurring Tasks, Due Dates & Time Reminders) features in the Todo Chatbot, integrate event-driven architecture with Kafka and full Dapr, and deploy to Minikube then cloud Kubernetes (DigitalOcean DOKS preferred).
Core Principles:

All implementation MUST explicitly invoke the relevant Phase 5 skills defined in SKILL.md:
→ "event-driven-architect" skill for Kafka event patterns and microservices design
→ "kafka-stream-processing" skill for publishing/consuming events (task-events, reminders, task-updates topics)
→ "convex-actions-scheduling" skill for recurring tasks and due-date reminder scheduling
→ "fastapi-microservices-development" skill for building decoupled services (e.g., Notification Service, Recurring Task Service)
→ "fastapi" skill for backend API extensions
→ "kubernetes" skill for Helm upgrades, Dapr components, and cloud deployment manifests
Use Dapr fully: Pub/Sub (Kafka component), State (PostgreSQL/Neon), Bindings (cron/jobs for reminders), Secrets, Service Invocation.
Prefer Redpanda Cloud (free tier) or self-hosted Kafka via Strimzi/Redpanda operator.
Deploy first to Minikube (extend Phase 4 Helm chart), then to cloud K8s.
Resource limits: CPU < 700m, memory < 1Gi per pod. Probes required.
All changes must trace to tasks and explicitly reference the skills used.
Prepare CI/CD hints for bonus (GitHub Actions).
labels: ["constitution", "update", "phase5", "event-driven", "dapr", "kafka", "kubernetes"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
- .specify/memory/constitution.md
- .specify/templates/plan-template.md
tests:
- null
---

## Prompt

/sp.constitution Implement all Intermediate (Priorities, Tags/Categories, Search & Filter, Sort) and Advanced (Recurring Tasks, Due Dates & Time Reminders) features in the Todo Chatbot, integrate event-driven architecture with Kafka and full Dapr, and deploy to Minikube then cloud Kubernetes (DigitalOcean DOKS preferred).
Core Principles:

All implementation MUST explicitly invoke the relevant Phase 5 skills defined in SKILL.md:
→ "event-driven-architect" skill for Kafka event patterns and microservices design
→ "kafka-stream-processing" skill for publishing/consuming events (task-events, reminders, task-updates topics)
→ "convex-actions-scheduling" skill for recurring tasks and due-date reminder scheduling
→ "fastapi-microservices-development" skill for building decoupled services (e.g., Notification Service, Recurring Task Service)
→ "fastapi" skill for backend API extensions
→ "kubernetes" skill for Helm upgrades, Dapr components, and cloud deployment manifests
Use Dapr fully: Pub/Sub (Kafka component), State (PostgreSQL/Neon), Bindings (cron/jobs for reminders), Secrets, Service Invocation.
Prefer Redpanda Cloud (free tier) or self-hosted Kafka via Strimzi/Redpanda operator.
Deploy first to Minikube (extend Phase 4 Helm chart), then to cloud K8s.
Resource limits: CPU < 700m, memory < 1Gi per pod. Probes required.
All changes must trace to tasks and explicitly reference the skills used.
Prepare CI/CD hints for bonus (GitHub Actions).

## Response snapshot

Updated the project constitution (`.specify/memory/constitution.md`) to version 2.0.0, reflecting the new Phase 5 principles for event-driven architecture, Dapr integration, Kafka, staged deployment, resource management, and traceability. Also updated the `plan-template.md` to include new constitution checks.

## Outcome

- ✅ Impact: Project constitution updated to v2.0.0, aligning with Phase 5 principles. `plan-template.md` updated with new constitution checks.
- 🧪 Tests: N/A (no tests were run or modified in this task)
- 📁 Files: `.specify/memory/constitution.md`, `.specify/templates/plan-template.md`
- 🔁 Next prompts: N/A
- 🧠 Reflection: The shell command for PHR creation failed, requiring a fallback to agent-native file writing.

## Evaluation notes (flywheel)

- Failure modes observed: `run_shell_command` with `bash` failed due to "No such file or directory".
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Investigate `run_shell_command` behavior with `bash` on current environment or ensure `create-phr.sh` is compatible with `powershell`.
