# Data Model: CLI Todo Application

## Task Entity

### Fields
- **id**: int - Unique identifier for the task (auto-generated)
- **title**: str - Title of the task (required, non-empty)
- **description**: str - Detailed description of the task (optional, can be empty)
- **status**: bool - Completion status (False = incomplete [ ], True = complete [x])

### Validation Rules
- Title must be provided and not empty
- ID must be unique within the task list
- Description can be empty but must be a string if provided
- Status defaults to False (incomplete) when creating a new task

### State Transitions
- Task status can transition from False (incomplete) to True (complete) when marked as done
- Task status can transition from True (complete) to False (incomplete) when unmarked

## TaskStore (In-Memory)

### Operations
- **create_task(title: str, description: str) -> Task**: Creates a new task with unique ID and incomplete status
- **get_all_tasks() -> List[Task]**: Returns all tasks in the store
- **get_task_by_id(task_id: int) -> Task**: Retrieves a specific task by ID
- **update_task(task_id: int, title: str = None, description: str = None) -> Task**: Updates task details
- **toggle_task_status(task_id: int) -> Task**: Toggles the completion status of a task
- **delete_task(task_id: int) -> bool**: Removes a task from the store

### Validation Rules
- Cannot create a task with empty title
- Cannot update a task with non-existent ID
- Cannot toggle status of a task with non-existent ID
- Cannot delete a task with non-existent ID
- Cannot get a task with non-existent ID