<!-- SYNC IMPACT REPORT
Version change: 1.0.0 → 1.1.0
Modified principles: Spec-Driven Development → Spec-Driven Development from Scratch, Reusable Intelligence Over Reimplementation → Reusable Intelligence Policy, Independent Verification → Reusable Intelligence Policy, User-Scoped Authentication → Authentication Requirement
Added sections: Core Invariants, Reusable Intelligence Policy, Architectural Invariants, Security Invariants
Removed sections: Independent Verification (merged into other sections)
Templates requiring updates: .specify/templates/plan-template.md, .specify/templates/spec-template.md, .specify/templates/tasks-template.md, .specify/templates/commands/*.md ✅ updated
Follow-up TODOs: None
-->

# Spec-Driven Full-Stack App Constitution

## Core Invariants

### I. Built from Scratch
This project is built entirely from scratch. No pre-existing application code is leveraged; all components are developed specifically for this implementation.

### II. Spec-Kit Plus Workflow
All development follows the Spec-Kit Plus workflow. Every feature must be specified, planned, and task-broken down before implementation begins.

### III. Claude Code Only
No manual coding is performed outside Claude Code. All code generation, modification, and management is performed through Claude Code tools and processes.

## Reusable Intelligence Policy

### I. Preferred Over Reimplementation
Reusable intelligence should be preferred over re-deriving solutions. When existing patterns, components, or solutions exist, they should be leveraged rather than recreated to maintain consistency and reduce redundancy.

### II. Project-Local Skills Priority
Project-local skills take priority over plugin or user skills. When a skill clearly matches a task's intent, it should be used. If a skill is not applicable, the reason should be implicit in the output.

### III. Skill Intent Matching
Skills are applied only when they match the task intent. The appropriateness of skill usage should be evaluated based on the specific requirements and context of each task.

## Architectural Invariants

### I. Service Separation
Frontend and backend are separate services. Each component maintains independent deployability while enabling coordinated development and operation.

### II. Authentication Requirement
Authentication is mandatory for all user-scoped operations. Every user action that accesses or modifies personal data must be authenticated and authorized.

### III. Persistent Storage Requirement
Persistent storage is required for all user data. All user-generated content must be stored durably and reliably.

## Security Invariants

### I. API Authentication Requirement
All API endpoints require authentication. Requests without valid credentials must return HTTP 401 status code, ensuring that no unauthenticated access is permitted.

### II. Data Access Isolation
Users may only access their own data. Strong data isolation is enforced at both the application and database levels to prevent cross-user data access.

### III. Credential Validation
All requests must include valid authentication credentials. Invalid or missing credentials result in access denial with appropriate error responses.

## Governance

All development activities must comply with this constitution. Changes to these principles require explicit documentation and approval. The constitution serves as the authoritative guide for development decisions and architectural choices.

**Version**: 1.1.0 | **Ratified**: 2026-01-06 | **Last Amended**: 2026-01-06