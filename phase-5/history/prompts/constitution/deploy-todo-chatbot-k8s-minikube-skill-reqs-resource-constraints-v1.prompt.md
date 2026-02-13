---
id: constitution_deploy_todo_chatbot_k8s_minikube_skill_reqs_resource_constraints_v1
title: Deploy Todo Chatbot to K8s Minikube with Skill Requirements
stage: constitution
date: 2026-02-04
tags: [kubernetes, minikube, deployment, skills, containerization, helm]
---

# Constitution Update: Phase 3 Todo Chatbot Deployment to Local Kubernetes on Minikube with Skill Usage Requirements and Resource Constraints

## PROMPT_TEXT

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
All code/config must trace to tasks and skills.

## RESPONSE_TEXT

Updated the constitution to reflect the new requirements for deploying the Phase 3 Todo Chatbot to local Kubernetes on Minikube. The updated constitution now includes:

1. System constraints that explicitly require using specific Phase 4 skills for containerization, Helm charting, and deployment
2. Core invariants emphasizing the skill-first approach
3. Architectural invariants covering containerization requirements, Helm chart requirements, Minikube deployment orchestration, resource constraints enforcement, and Dapr preparation for Phase 5
4. Security invariants including infrastructure spec validation
5. Updated governance section reflecting the new skill-based approach

The version was incremented from 1.2.0 to 1.3.0, with the constitution now titled "Kubernetes Deployment Constitution" instead of "Conversational AI Layer Constitution" to better reflect the new focus on Kubernetes deployment with specific skill usage requirements and resource constraints.