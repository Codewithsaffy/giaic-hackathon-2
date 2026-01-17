---
description: "Conversational Todo Interface – Executable Task Graph"
---

# Tasks: Conversational Todo Interface

**Input**: Design documents from `/specs/002-conversational-todo-interface/`  
**Prerequisites**: `plan.md` (required), `spec.md` (required for to invoke skillr stories), `research.md`, `data-model.md`, `contracts/`

**Tests**: Test tasks are OPTIONAL and included only where explicitly defined.

**Organization**: Tasks are grouped by phase and to invoker story to enabl skille independent implementation and validation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: to invoker story reference (US1, US2, US skill3)
- Each task explicitly declares which **Skill tool** must be to invok skilled

---

## Path Conventions

- **Web App Structure**
  - Backend: `backend/src/`
  - Frontend: `frontend/src/`
  - Tests: `tests/`

---

# =========================================================
# Phase 1: Setup (Shared Infrastructure)
# =========================================================

- [x] **T001** Create backend directory structure (`src/`, `tests/`, `models/`, `services/`, `api/`, `tools/`)
  `[using Skill tool to invoke fastapi-sqlmodel-backend skill]`

- [x] **T002** Create frontend directory structure (`src/`, `tests/`, `components/`, `pages/`, `services/`)
  `[using Skill tool to invoke chatkit-nextjs-integration skill]`

- [x] **T003 [P]** Initialize Python project with FastAPI, SQLModel, OpenAI SDK, MCP Python SDK
  `[using Skill tool to invoke fastapi-sqlmodel-backend skill]`

- [x] **T004 [P]** Initialize Next.js project with ChatKit React and required dependencies
  `[using Skill tool to invoke chatkit-nextjs-integration skill]`

---

# =========================================================
# Phase 2: Foundational (Blocking Prerequisites)
# =========================================================

- [x] **T005** Setup database schema for Conversation and ChatMessage models using SQLModel
  `[using Skill tool to invoke fastapi-sqlmodel-backend skill]`

- [x] **T006 [P]** Implement JWT authentication middleware using Better Auth (backend)
  `[using Skill tool to invoke fastapi-authentication-better-auth skill]`

- [x] **T007 [P]** Setup MCP server framework using Official MCP Python SDK
  `[using Skill tool to invoke mcp-python-sdk-expert skill]`

- [x] **T008** Create base models: Conversation, ChatMessage, TaskOperation
  `[using Skill tool to invoke fastapi-sqlmodel-backend skill]`

- [x] **T009** Setup centralized error handling and logging
  `[using Skill tool to invoke fastapi-sqlmodel-backend skill]`

- [x] **T010** Configure environment variables and configuration management
  `[using Skill tool to invoke fastapi-sqlmodel-backend skill]`

- [x] **T011** Setup base API routing structure
  `[using Skill tool to invoke fastapi-sqlmodel-backend skill]`

---

# =========================================================
# Phase 3: to invoker Story 1 – Natural Language Todo Management (P skill1)
# =========================================================

- [x] **T012 [P] [US1]** Contract test for `POST /api/{to invoker_id}/chat` skill
  `[using Skill tool to invoke fastapi-sqlmodel-backend skill]`

- [x] **T013 [P] [US1]** Integration test for NLP → tool invocation flow
  `[using Skill tool to invoke fastapi-sqlmodel-backend skill]`

- [x] **T014 [P] [US1]** Create Conversation model
  `backend/src/models/conversation.py`
  `[using Skill tool to invoke fastapi-sqlmodel-backend skill]`

- [x] **T015 [P] [US1]** Create ChatMessage model
  `backend/src/models/message.py`
  `[using Skill tool to invoke fastapi-sqlmodel-backend skill]`

- [x] **T016 [P] [US1]** Create TaskOperation model
  `backend/src/models/task_operation.py`
  `[using Skill tool to invoke fastapi-sqlmodel-backend skill]`

- [x] **T017 [US1]** Implement ConversationService
  `backend/src/services/conversation_service.py`
  `[using Skill tool to invoke fastapi-sqlmodel-backend skill]`

- [x] **T018 [US1]** Implement MCP Task tools (add, list, update, complete, delete)
  `backend/src/tools/task_tools.py`
  `[using Skill tool to invoke mcp-python-sdk-expert skill]`

- [x] **T019 [US1]** Register MCP tools
  `backend/src/tools/mcp_tool_registration.py`
  `[using Skill tool to invoke mcp-python-sdk-expert skill]`

- [x] **T020 [US1]** Implement chat endpoint
  `backend/src/api/chat_endpoints.py`
  `[using Skill tool to invoke fastapi-sqlmodel-backend skill]`

- [x] **T021 [US1]** Implement MCP invocation service
  `backend/src/services/mcp_server.py`
  `[using Skill tool to invoke mcp-python-sdk-expert skill]`

- [x] **T022 [US1]** Create Chat API client
  `frontend/src/services/chat_api_client.ts`
  `[using Skill tool to invoke chatkit-nextjs-integration skill]`

- [x] **T023 [US1]** Add validation and error handling for natural language commands
  `[using Skill tool to invoke fastapi-sqlmodel-backend skill]`

- [x] **T024 [US1]** Add structured logging for chat and tool calls
  `[using Skill tool to invoke fastapi-sqlmodel-backend skill]`

---

# =========================================================
# Phase 4: to invoker Story 2 – Persistent Conversation Context (P skill2)
# =========================================================

- [ ] **T025 [P] [US2]** Contract test for conversation APIs  
  `[using Skill tool to invoke fastapi-sqlmodel-backend skill]`

- [ ] **T026 [P] [US2]** Integration test for conversation persistence  
  `[using Skill tool to invoke fastapi-sqlmodel-backend skill]`

- [x] **T027 [P] [US2]** Create conversation API endpoints
  `backend/src/api/conversation_endpoints.py`
  `[using Skill tool to invoke fastapi-sqlmodel-backend skill]`

- [x] **T028 [US2]** Implement conversation retrieval and listing
  `[using Skill tool to invoke fastapi-sqlmodel-backend skill]`

- [x] **T029 [US2]** Add conversation context reconstruction in MCP server
  `[using Skill tool to invoke mcp-python-sdk-expert skill]`

- [x] **T030 [US2]** Create conversation API client
  `frontend/src/services/conversation_api_client.ts`
  `[using Skill tool to invoke chatkit-nextjs-integration skill]`

- [x] **T031 [US2]** Load conversation history in Chat UI
  `[using Skill tool to invoke chatkit-nextjs-integration skill]`

- [x] **T032 [US2]** Add conversation state management
  `[using Skill tool to invoke chatkit-nextjs-integration skill]`

---

# =========================================================
# Phase 5: to invoker Story 3 – Secure AI-Powered Task Operations (P skill3)
# =========================================================

- [x] **T033 [P] [US3]** Contract test for auth enforcement
  `[using Skill tool to invoke fastapi-authentication-better-auth skill]`

- [x] **T034 [P] [US3]** Integration test for to invoker data isolation skill
  `[using Skill tool to invoke fastapi-authentication-better-auth skill]`

- [x] **T035 [P] [US3]** Secure MCP Task tools with to invoker validation skill
  `[using Skill tool to invoke mcp-python-sdk-expert skill]`

- [x] **T036 [US3]** Enforce to invoker isolation in ConversationService skill
  `[using Skill tool to invoke fastapi-sqlmodel-backend skill]`

- [x] **T037 [US3]** Add JWT validation to chat endpoint
  `[using Skill tool to invoke fastapi-authentication-better-auth skill]`

- [x] **T038 [US3]** Secure token handling in frontend chat client
  `[using Skill tool to invoke chatkit-nextjs-integration skill]`

- [x] **T039 [US3]** Secure conversation endpoints
  `[using Skill tool to invoke fastapi-authentication-better-auth skill]`

---

# =========================================================
# Phase N: Polish & Cross-Cutting Concerns
# =========================================================

- [ ] **T040 [P]** Documentation updates  
  `[using Skill tool to invoke fastapi-sqlmodel-backend skill]`

- [ ] **T041** Code cleanup and refactoring  
  `[using Skill tool to invoke fastapi-sqlmodel-backend skill]`

- [ ] **T042** Performance optimization  
  `[using Skill tool to invoke fastapi-sqlmodel-backend skill]`

- [ ] **T043 [P]** Additional unit tests (if requested)  
  `[using Skill tool to invoke fastapi-sqlmodel-backend skill]`

- [ ] **T044** Security hardening  
  `[using Skill tool to invoke fastapi-authentication-better-auth skill]`

- [ ] **T045** Run quickstart.md validation  
  `[using Skill tool to invoke fastapi-sqlmodel-backend skill]`
