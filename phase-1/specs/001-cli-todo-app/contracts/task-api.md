# Task API Contracts: CLI Todo Application

## Task Data Contract

### Task Object
```python
class Task:
    id: int          # Unique identifier
    title: str       # Task title (non-empty)
    description: str # Task description (optional)
    status: bool     # Completion status (True=complete, False=incomplete)
```

## Store Interface Contract

### Methods

#### `create_task(title: str, description: str = "") -> Task`
- **Purpose**: Create a new task with unique ID and incomplete status
- **Preconditions**:
  - `title` must be non-empty string
- **Postconditions**:
  - Returns Task object with unique ID
  - Task status is False (incomplete)
  - Task is added to the store
- **Errors**:
  - ValueError if title is empty

#### `get_all_tasks() -> List[Task]`
- **Purpose**: Retrieve all tasks from the store
- **Preconditions**: None
- **Postconditions**:
  - Returns list of all Task objects
  - Returns empty list if no tasks exist
- **Errors**: None

#### `get_task_by_id(task_id: int) -> Task`
- **Purpose**: Retrieve a specific task by ID
- **Preconditions**:
  - Task with `task_id` must exist
- **Postconditions**:
  - Returns the Task object with matching ID
- **Errors**:
  - ValueError if task with `task_id` does not exist

#### `update_task(task_id: int, title: str = None, description: str = None) -> Task`
- **Purpose**: Update existing task details
- **Preconditions**:
  - Task with `task_id` must exist
  - If `title` is provided, it must be non-empty
- **Postconditions**:
  - Returns updated Task object
  - Task details are updated in the store
- **Errors**:
  - ValueError if task with `task_id` does not exist
  - ValueError if `title` is provided but is empty

#### `toggle_task_status(task_id: int) -> Task`
- **Purpose**: Toggle the completion status of a task
- **Preconditions**:
  - Task with `task_id` must exist
- **Postconditions**:
  - Returns Task object with toggled status
  - Task status is updated in the store
- **Errors**:
  - ValueError if task with `task_id` does not exist

#### `delete_task(task_id: int) -> bool`
- **Purpose**: Remove a task from the store
- **Preconditions**:
  - Task with `task_id` must exist
- **Postconditions**:
  - Returns True if task was deleted
  - Task is removed from the store
- **Errors**:
  - ValueError if task with `task_id` does not exist