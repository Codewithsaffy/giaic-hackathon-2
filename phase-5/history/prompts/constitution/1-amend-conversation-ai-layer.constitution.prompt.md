---
id: 1
title: "Amend Constitution to Add Conversational AI Layer"
stage: constitution
date_iso: "2026-01-14"
surface: "agent"
model: "Claude Sonnet 4.5"
feature: "conversational-ai-layer"
branch: "main"
user: "user"
command: "sp.constitution"
labels:
  - "constitution"
  - "conversational-ai"
  - "layered-architecture"
  - "mcp-tools"
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml:
  - ".specify/memory/constitution.md"
tests_yaml: []
---

# Amendment to Project Constitution: Conversational AI Layer

## Original Prompt

```text
# Constitution — Conversational AI Layer

## System Constraints

1. This layer EXTENDS the existing Full-Stack Todo Web Application.
2. Existing authentication, UI, REST APIs, and database models MUST NOT be rewritten.
3. All task operations MUST reuse existing task services.
4. MCP tools MUST be stateless.
5. FastAPI server MUST remain stateless.
6. Conversation context MUST persist only in the database.
7. AI agents MUST interact with the system exclusively through MCP tools.
8. No manual coding — implementation via Claude Code only.

## Mandatory Skills

- OpenAI Agents SDK Expert
- MCP Python SDK Expert
- FastAPI + SQLModel Backend
- ChatKit + Next.js Integration
- FastAPI Authentication (reuse)

## Architectural Principles

- Layered architecture
- Thin MCP tools
- Agent as decision-maker
- Database as single source of truth
```

## Response Summary

Updated the project constitution to incorporate the Conversational AI Layer requirements while maintaining compatibility with the existing Todo Web Application. The new constitution includes:

- System constraints for extending the existing application
- Layered architecture principles
- MCP tool integration requirements
- Statelessness requirements for both MCP tools and FastAPI server
- Enhanced security invariants for MCP tools
- Preservation of existing principles like Claude Code only and Spec-Kit Plus workflow

## Outcome

Successfully updated `.specify/memory/constitution.md` from version 1.1.0 to 1.2.0 with the new Conversational AI Layer constitution. The update includes a comprehensive Sync Impact Report showing the changes made, with appropriate versioning and governance information.

## Evaluation

The updated constitution properly extends the existing application while enforcing the required constraints for the Conversational AI Layer, including MCP tool usage, statelessness requirements, and layered architecture principles.