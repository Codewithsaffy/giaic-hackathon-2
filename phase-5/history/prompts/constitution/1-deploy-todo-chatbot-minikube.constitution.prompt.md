---
id: 1
title: Deploy Todo Chatbot to Minikube
stage: constitution
date_iso: 2026-02-04
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: user
command: sp.constitution
labels: ["kubernetes", "minikube", "deployment", "containerization"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml: []
tests_yaml: []
---

# Deploy Todo Chatbot to Minikube

## Original Prompt
Deploy the Phase 3 Todo Chatbot to local Kubernetes on Minikube.
Core Principles:

All containerization, Helm charting, and deployment must be performed by invoking the specific Phase 4 skills defined in SKILL.md.
Explicitly use:
→ "Docker Containerization" skill for Dockerfiles and Gordon integration
→ "Helm Chart Generation" skill for Chart.yaml, values.yaml, and templates
→ "Minikube Local Deployment Orchestration" skill for deployment sequence and AIOps commands
→ "Infrastructure Spec Validation" skill before finalizing any implementation
→ "Blueprint Creation" skill for bonus reusable artifacts
Never write Docker/Helm/K8s configs without referencing the relevant skill.
Skills are the single source of truth for patterns and best practices.
Resource limits: CPU < 500m, memory < 512Mi. Readiness/liveness probes required.
Prepare Dapr annotations for Phase 5.
All code/config must trace to tasks and skill

## Response Summary
Updated the project constitution at .specify/memory/constitution.md to reflect the requirements for deploying the Phase 3 Todo Chatbot to local Kubernetes on Minikube. The constitution now includes:

- System Constraints requiring use of specific Phase 4 skills for containerization, Helm charting, and deployment
- Core Invariants enforcing skill-first approach and Claude Code usage
- Architectural Invariants covering containerization, Helm charts, Minikube deployment, resource constraints, and Dapr preparation
- Security Invariants ensuring proper authentication and data isolation
- Governance requirements for compliance with the updated constitution

The constitution version has been updated to reflect these changes and includes all specified requirements including resource limits (CPU < 500m, memory < 512Mi) and readiness/liveness probe requirements.

## Outcome
Successfully updated the project constitution to guide the deployment of the Todo Chatbot to Minikube with proper constraints and skill usage requirements.