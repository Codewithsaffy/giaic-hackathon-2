# Implementation Plan: Conversational Todo Interface

**Branch**: `002-conversational-todo-interface` | **Date**: 2026-01-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-conversational-todo-interface/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implementation of a conversational AI layer that enables users to manage todos using natural language. The solution includes an MCP server exposing task management tools to an OpenAI Agent, a stateless chat API endpoint, persistent conversation storage, and ChatKit-based UI integration. The system extends the existing todo application while reusing authentication and backend services.

## Technical Context

**Language/Version**: Python 3.11, TypeScript/JavaScript for frontend
**Primary Dependencies**: FastAPI, SQLModel, OpenAI SDK, MCP Python SDK, ChatKit React component, Better Auth
**Storage**: PostgreSQL (Neon Serverless) for conversation and message persistence
**Testing**: pytest for backend, Jest for frontend
**Target Platform**: Web application (Next.js 16+ with App Router)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: <3 second response time for 95% of chat interactions, 90% natural language command accuracy
**Constraints**: Must reuse existing authentication and backend services, MCP tools must be stateless, conversation context persisted only in database
**Scale/Scope**: Support for existing user base with individual conversation contexts

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Based on constitution file (Initial Check):

- ✅ Layered Architecture: Building as extension to existing application
- ✅ Service Separation: Frontend and backend remain separate services
- ✅ Authentication Requirement: Using existing JWT-based authentication
- ✅ MCP Tool Integration: AI agents interact through MCP tools exclusively
- ✅ Statelessness Requirement: MCP tools and FastAPI server remain stateless
- ✅ Data Access Isolation: Users can only access their own conversations and tasks
- ✅ MCP Tool Security: Following security best practices for tool invocations

Based on constitution file (Post-Design Check):

- ✅ Layered Architecture: Solution extends existing application without modifying core components
- ✅ Service Separation: Clear separation maintained between frontend and backend services
- ✅ Authentication Requirement: Leveraging existing JWT authentication system
- ✅ MCP Tool Integration: AI agents exclusively use MCP tools for task operations
- ✅ Statelessness Requirement: Chat API is stateless with conversation context from DB
- ✅ Data Access Isolation: Database models enforce user-specific data access
- ✅ MCP Tool Security: Tools follow security best practices with authentication
- ✅ Reusable Intelligence: Reusing existing task services and authentication

## Project Structure

### Documentation (this feature)

```text
specs/002-conversational-todo-interface/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── conversation.py
│   │   └── message.py
│   ├── services/
│   │   ├── conversation_service.py
│   │   ├── task_service.py (reused from existing)
│   │   └── mcp_server.py
│   ├── api/
│   │   ├── chat_endpoints.py
│   │   └── auth_middleware.py (reused from existing)
│   └── tools/
│       ├── task_tools.py
│       └── mcp_tool_registration.py
└── tests/
    ├── unit/
    ├── integration/
    └── contract/

frontend/
├── src/
│   ├── components/
│   │   ├── ChatInterface.tsx
│   │   └── ChatKitWrapper.tsx
│   ├── pages/
│   │   └── chat.tsx
│   └── services/
│       └── chat_api_client.ts
└── tests/
    ├── unit/
    └── integration/
```

**Structure Decision**: Web application structure with separate backend and frontend directories to maintain service separation while enabling coordinated development. Backend contains new conversation-related models and services alongside reused task services. Frontend adds chat interface components that integrate with existing authentication and coexist with current UI.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
