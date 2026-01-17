<!-- SYNC IMPACT REPORT
Version change: 1.1.0 → 1.2.0
Modified principles: Spec-Driven Full-Stack App Constitution → Conversational AI Layer Constitution with new system constraints and architectural invariants
Added sections: System Constraints section, MCP Tool Integration invariant, Statelessness Requirement invariant, MCP Tool Security invariant
Removed sections: Built from Scratch invariant (replaced with layered architecture approach)
Templates requiring updates: .specify/templates/plan-template.md, .specify/templates/spec-template.md, .specify/templates/tasks-template.md ✅ reviewed for consistency
Follow-up TODOs: None
-->

# Conversational AI Layer Constitution

## System Constraints

1. This layer EXTENDS the existing Full-Stack Todo Web Application.
2. Existing authentication, UI, REST APIs, and database models MUST NOT be rewritten.
3. All task operations MUST reuse existing task services.
4. MCP tools MUST be stateless.
5. FastAPI server MUST remain stateless.
6. Conversation context MUST persist only in the database.
7. AI agents MUST interact with the system exclusively through MCP tools.
8. No manual coding — implementation via Claude Code only.

## Core Invariants

### I. Layered Architecture
The Conversational AI Layer is built as an extension to the existing application. It integrates seamlessly with existing components while maintaining clear separation of concerns.

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

### I. Service Separation
Frontend and backend are separate services. Each component maintains independent deployability while enabling coordinated development and operation.

### II. Authentication Requirement
Authentication is mandatory for all user-scoped operations. Every user action that accesses or modifies personal data must be authenticated and authorized.

### III. MCP Tool Integration
AI agents interact with the system exclusively through MCP tools, ensuring standardized communication and consistent behavior.

### IV. Statelessness Requirement
Both MCP tools and FastAPI server maintain statelessness, with all conversation context persisted only in the database.

## Security Invariants

### I. API Authentication Requirement
All API endpoints require authentication. Requests without valid credentials must return HTTP 401 status code, ensuring that no unauthenticated access is permitted.

### II. Data Access Isolation
Users may only access their own data. Strong data isolation is enforced at both the application and database levels to prevent cross-user data access.

### III. Credential Validation
All requests must include valid authentication credentials. Invalid or missing credentials result in access denial with appropriate error responses.

### IV. MCP Tool Security
MCP tools must follow security best practices, with proper authentication and authorization for all tool invocations.

## Governance

All development activities must comply with this constitution. Changes to these principles require explicit documentation and approval. The constitution serves as the authoritative guide for development decisions and architectural choices.

**Version**: 1.2.0 | **Ratified**: 2026-01-06 | **Last Amended**: 2026-01-14