---

description: "Task list for Intermediate & Advanced Todo Chatbot Features"
---

# Tasks: Intermediate & Advanced Todo Chatbot Features

**Input**: Design documents from `specs/1-todo-chatbot-features/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are included as part of implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Paths shown below assume multi-service backend structure as defined in `plan.md`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project directory structure for `1-todo-chatbot-features` in `specs/1-todo-chatbot-features/`
- [x] T002 Initialize Python project with FastAPI and Dapr SDK dependencies in `src/`.
- [x] T003 [P] Configure linting and formatting tools (e.g., Black, Flake8) for the project in `pyproject.toml` or `.pre-commit-config.yaml`.
- [x] T004 [P] Setup shared utilities/models directory in `src/shared/`.
- [x] T005 [P] Configure Dapr components directory in `deploy/dapr-components/`.
- [x] T006 [P] Configure Helm chart directory in `deploy/helm/`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T007 Implement base SQLModel for common fields (UUID, created_at, updated_at) in `src/shared/models.py`.
- [x] T008 [P] Configure Dapr Pub/Sub component for Redis in `deploy/dapr-components/pubsub.yaml`.
- [x] T009 [P] Configure Dapr State Store component for Redis in `deploy/dapr-components/statestore.yaml`.
- [x] T010 [P] Configure Dapr Secrets component in `deploy/dapr-components/secrets.yaml`.
- [x] T011 [P] Setup error handling and logging infrastructure for microservices in `src/shared/`.
- [x] T012 [P] Setup common Dapr client and service invocation utility in `src/shared/utils.py`.

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Manage Task Priorities (P1) 🎯 MVP

**Goal**: Allow users to assign, view, and modify priority levels for their tasks.

**Independent Test**: Create a task, set its priority, view the task to confirm priority, and update its priority, all via chatbot commands.

### Implementation for User Story 1

- [x] T013 [P] [US1] Update Task model (add `priority` Enum) in `src/shared/models.py`.
- [x] T014 [US1] Extend Task Service with priority management logic in `src/task_service/services/task_priority_service.py`.
- [x] T015 [US1] Implement API endpoint for setting task priority in `src/task_service/api/task_api.py`.
- [x] T016 [US1] Integrate chatbot command processing for "set priority" in `src/api_gateway/nl_processor.py`.
- [x] T017 [US1] Update Task Service to publish `task_updated` event on priority change to `task-events` topic in `src/task_service/events/task_events.py`.

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Tag and Categorize Tasks (P1)

**Goal**: Allow users to add multiple tags or categories to their tasks for flexible organization and retrieval.

**Independent Test**: Create a task, add tags to it, view the task to confirm tags, and filter tasks by tags, all via chatbot commands.

### Implementation for User Story 2

- [x] T018 [P] [US2] Update Task model (add `tags` Array of Strings) in `src/shared/models.py`.
- [x] T019 [US2] Extend Task Service with tag management logic in `src/task_service/services/task_tag_service.py`.
- [x] T020 [US2] Implement API endpoint for adding/removing task tags in `src/task_service/api/task_api.py`.
- [x] T021 [US2] Integrate chatbot command processing for "add tag" in `src/api_gateway/nl_processor.py`.
- [x] T022 [US2] Update Task Service to publish `task_updated` event on tag change to `task-events` topic in `src/task_service/events/task_events.py`.

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Search, Filter, and Sort Tasks (P1)

**Goal**: Allow users to quickly find specific tasks by searching keywords, filtering by criteria like priority or tags, and sorting by different attributes.

**Independent Test**: Perform various search, filter, and sort operations on a diverse set of tasks via chatbot commands.

### Implementation for User Story 3

- [x] T023 [US3] Extend Task Service with search/filter logic based on description, priority, tags in `src/task_service/services/task_query_service.py`.
- [x] T024 [US3] Extend Task Service with sorting logic (by creation date, due date, priority) in `src/task_service/services/task_query_service.py`.
- [x] T025 [US3] Implement API endpoint for searching, filtering, and sorting tasks in `src/task_service/api/task_api.py`.
- [x] T026 [US3] Integrate chatbot command processing for "find task", "show tasks by", "sort tasks" in `src/api_gateway/nl_processor.py`.

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: User Story 4 - Create Recurring Tasks (P2)

**Goal**: Allow users to create tasks that automatically repeat based on a defined schedule.

**Independent Test**: Create a recurring task, verify new instances are created automatically according to the schedule, and manage the series via chatbot commands.

### Implementation for User Story 4

- [x] T027 [P] [US4] Update Task model (add `recurrence_pattern` String) in `src/shared/models.py`.
- [x] T028 [P] [US4] Create Recurring Task Service microservice scaffolding in `src/recurring_task_service/`.
- [x] T029 [US4] Implement API endpoint for creating/managing recurring tasks in `src/recurring_task_service/api/recurring_task_api.py`.
- [x] T030 [US4] Implement recurring task scheduling logic in `src/recurring_task_service/services/scheduler.py` (using Dapr Bindings/Jobs API).
- [x] T031 [US4] Recurring Task Service: publish `recurring_task_instance_created` event to `task-updates` topic in `src/recurring_task_service/events/recurring_events.py`.
- [x] T032 [US4] Integrate chatbot command processing for "create recurring task" in `src/api_gateway/nl_processor.py`.

**Checkpoint**: At this point, User Stories 1 to 4 should be functional

---

## Phase 7: User Story 5 - Set Due Dates and Reminders (P2)

**Goal**: Allow users to assign specific due dates and times to tasks and receive notifications.

**Independent Test**: Set a due date/time for a task, configure a reminder, and verify that a notification is received at the specified reminder time.

### Implementation for User Story 5

- [x] T033 [P] [US5] Update Task model (add `due_date` DateTime, `remind_at` DateTime, `recurring_interval` String) in `src/shared/models.py`.
- [x] T034 [P] [US5] Create Notification Service microservice scaffolding in `src/notification_service/main.py`.
- [x] T035 [US5] Implement reminder triggering logic using Dapr Jobs API in `backend/api/todos.py`.
- [x] T036 [US5] Notification Service: subscribe to `reminders` topic.
- [x] T037 [US5] Task Service: publish to `reminders` topic when task has `remind_at` set.
- [x] T038 [US5] Integrate chatbot command processing for "remind me" in NL gateway logic.

**Checkpoint**: At this point, User Stories 1 to 5 should be functional

---

## Phase 8: User Story 6 - Event-Driven Operations (P3)

**Goal**: Ensure task-related actions are processed as events flowing through Kafka, handled by dedicated microservices.

**Independent Test**: Perform a task action (e.g., creating a task) and verify that the corresponding event is published to, and consumed from, the appropriate Kafka topic by the relevant microservice.

### Implementation for User Story 6

- [x] T040 [P] [US6] Refine event schemas for `task_created`, `task_updated` in `src/shared/models.py`.
- [x] T041 [US6] Implement Audit Service to consume `task-events` and `reminders` topics for centralized logging.
- [x] T042 [US6] Configure Dapr Pub/Sub bindings in `deploy/dapr-components/pubsub.yaml` using Redis.

**Checkpoint**: Event-driven architecture should be fully operational

---

## Phase 9: User Story 7 - Minikube Deployment and Verification (P3)

**Goal**: Deploy the complete system to Minikube and verify its functionality.

**Independent Test**: Deploy the extended Helm chart to Minikube, verify all pods are running and Dapr sidecars are injected, and then perform end-to-end functional tests.

### Implementation for User Story 7

- [x] T044 [P] [US7] Implement multi-service Dockerfile in `src/shared/Dockerfile.microservice`.
- [x] T045 [P] [US7] Create Kubernetes manifests for `notification-service`, `recurring-service`, and `audit-service` in `deploy/`.
- [x] T046 [P] [US7] Configure Dapr Jobs component for exact-time reminders in `deploy/dapr-components/jobs.yaml`.
- [x] T047 [US7] Deploy all components to Minikube and verify successful pod readiness and Dapr sidecar injection.

**Checkpoint**: Minikube deployment fully verified

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T051 [P] Document all API contracts (OpenAPI/Swagger) in `specs/1-todo-chatbot-features/contracts/`.
- [x] T052 [P] Refine `quickstart.md` with detailed deployment and interaction instructions `specs/1-todo-chatbot-features/quickstart.md`.
- [x] T053 [P] Implement comprehensive unit and integration tests for all new services and features in `src/tests/`.
- [x] T054 Optimize Dapr configurations and resource limits for all microservices in `deploy/helm/`.
- [x] T055 Prepare deployment manifests and detailed instructions for DigitalOcean DOKS in `deploy/cloud-k8s/doks-manifests.md`.
- [x] T056 Prepare CI/CD hints for GitHub Actions in `.github/workflows/ci-cd.yaml`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P1)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1/US2/US3 but should be independently testable
- **User Story 5 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1/US2/US3/US4 but should be independently testable
- **User Story 6 (P3)**: Can start after Foundational (Phase 2) - May integrate with prior US but should be independently testable
- **User Story 7 (P3)**: Can start after Foundational (Phase 2) - May integrate with prior US but should be independently testable

### Within Each User Story

- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Add User Story 6 → Test independently → Deploy/Demo
8. Add User Story 7 → Test independently → Deploy/Demo
9. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1, 2, 3
   - Developer B: User Story 4, 5
   - Developer C: User Story 6, 7
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
