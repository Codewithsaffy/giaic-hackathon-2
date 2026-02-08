---
name: Infrastructure Spec Validation
description: Validates infrastructure implementation against Phase 4 requirements and specs.
---

# Infrastructure Spec Validation

Before any implementation, validate against Phase 4 requirements:

- Containerization complete (Dockerfiles present)
- Helm chart functional (`helm template` succeeds)
- Local deployment works (chatbot accessible via Minikube tunnel)
- AIOps tools used (show `kubectl-ai`/`kagent` commands in output)
- All changes traceable to specs in `/specs/deployment/`
- If anything is missing, request spec update first.
