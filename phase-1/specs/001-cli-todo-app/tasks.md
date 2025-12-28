---
description: "Task list for CLI Todo application implementation"
---

# Tasks: CLI Todo Application

**Input**: Design documents from `/specs/001-cli-todo-app/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The feature specification requested pytest setup to verify the in-memory store logic, so test tasks are included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project structure with src/ and tests/ directories
- [X] T002 [P] Create pyproject.toml with Python 3.13+ requirement and uv dependency management
- [X] T003 [P] Create README.md with setup instructions per quickstart.md
- [X] T004 Create .python-version file specifying Python 3.13+

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Create Task dataclass in src/models.py with id, title, description, status fields
- [X] T006 Create TaskStore class in src/store.py with in-memory list storage
- [X] T007 [P] Implement TaskStore create_task method with validation per data-model.md
- [X] T008 [P] Implement TaskStore get_all_tasks method per data-model.md
- [X] T009 [P] Implement TaskStore get_task_by_id method with validation per data-model.md
- [X] T010 [P] Implement TaskStore update_task method with validation per data-model.md
- [X] T011 [P] Implement TaskStore toggle_task_status method per data-model.md
- [X] T012 [P] Implement TaskStore delete_task method with validation per data-model.md
- [X] T013 Create TaskStore singleton instance in src/store.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add and View Tasks (Priority: P1) 🎯 MVP

**Goal**: Users can add tasks with title and description, then view all tasks with ID, Title, Description, and Status

**Independent Test**: Can be fully tested by adding a task and viewing the list to confirm it appears with the correct status indicator. Delivers the fundamental value of task tracking.

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T014 [P] [US1] Create test_store.py with tests for create_task method in tests/test_store.py
- [X] T015 [P] [US1] Create test_store.py with tests for get_all_tasks method in tests/test_store.py
- [X] T016 [P] [US1] Create test_models.py with tests for Task dataclass in tests/test_models.py

### Implementation for User Story 1

- [X] T017 [US1] Implement CLI menu interface in src/cli.py with add_task function
- [X] T018 [US1] Implement CLI menu interface in src/cli.py with view_tasks function
- [X] T019 [US1] Connect CLI add_task to TaskStore create_task method
- [X] T020 [US1] Connect CLI view_tasks to TaskStore get_all_tasks method
- [X] T021 [US1] Format task display with ID, Title, Description, and Status ([ ] or [x]) per spec requirements

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Update and Complete Tasks (Priority: P2)

**Goal**: Users can update task details (title or description) by ID and toggle task completion status by ID

**Independent Test**: Can be tested by updating a task's details or toggling its status and verifying the change persists in the system.

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

- [X] T022 [P] [US2] Create tests for update_task method in tests/test_store.py
- [X] T023 [P] [US2] Create tests for toggle_task_status method in tests/test_store.py

### Implementation for User Story 2

- [X] T024 [US2] Implement CLI menu interface in src/cli.py with update_task function
- [X] T025 [US2] Implement CLI menu interface in src/cli.py with toggle_task_status function
- [X] T026 [US2] Connect CLI update_task to TaskStore update_task method
- [X] T027 [US2] Connect CLI toggle_task_status to TaskStore toggle_task_status method
- [X] T028 [US2] Add validation for update_task to handle empty title properly per data-model.md

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Delete Tasks (Priority: P3)

**Goal**: Users can delete a task permanently by ID

**Independent Test**: Can be tested by deleting a task and verifying it no longer appears in the task list.

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

- [X] T029 [P] [US3] Create tests for delete_task method in tests/test_store.py

### Implementation for User Story 3

- [X] T030 [US3] Implement CLI menu interface in src/cli.py with delete_task function
- [X] T031 [US3] Connect CLI delete_task to TaskStore delete_task method
- [X] T032 [US3] Add proper error handling for delete operations per spec requirements

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Main Entry Point and Runtime Verification

**Goal**: Create main entry point with Python 3.13+ verification and main menu loop

- [X] T033 Create main.py with Python 3.13+ version verification per spec FR-001
- [X] T034 Implement main menu loop in src/main.py that continues until user chooses to exit per spec FR-002
- [X] T035 Connect main menu to CLI functions per spec requirements
- [X] T036 Add graceful error handling for invalid inputs per spec FR-008 and FR-010

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T037 [P] Add docstrings to all functions in src/models.py, src/store.py, src/cli.py, src/main.py per constitution
- [X] T038 [P] Add type hints to all functions per constitution requirements
- [X] T039 Add comprehensive error handling for edge cases per spec (empty titles, invalid IDs, etc.)
- [X] T040 [P] Add additional unit tests for edge cases in tests/ directory
- [ ] T041 Run quickstart.md validation to ensure all setup instructions work

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Main Entry Point (Phase 6)**: Depends on all user stories being implemented
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Create test_store.py with tests for create_task method in tests/test_store.py"
Task: "Create test_store.py with tests for get_all_tasks method in tests/test_store.py"
Task: "Create test_models.py with tests for Task dataclass in tests/test_models.py"

# Launch all implementation tasks for User Story 1 together:
Task: "Implement CLI menu interface in src/cli.py with add_task function"
Task: "Implement CLI menu interface in src/cli.py with view_tasks function"
```

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
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
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