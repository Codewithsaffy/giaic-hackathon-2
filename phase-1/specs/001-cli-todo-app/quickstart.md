# Quickstart Guide: CLI Todo Application

## Prerequisites
- Python 3.13+ installed
- `uv` package manager installed

## Setup

1. Clone or create the project directory
2. Install dependencies using `uv`:
   ```bash
   uv sync
   # or if starting fresh
   uv pip install -r requirements.txt
   ```

## Project Structure
```
src/
├── models.py            # Task dataclass definition
├── store.py             # In-memory storage implementation
├── cli.py               # CLI interface and menu system
└── main.py              # Application entry point
tests/
├── test_store.py        # Store functionality tests
└── test_models.py       # Task model tests
pyproject.toml           # Project configuration and dependencies
```

## Running the Application

```bash
# Run the application directly
python src/main.py

# Or using a script alias if configured
uv run src/main.py
```

## Key Features

1. **Add Task**: Add a new task with title and description
2. **View Tasks**: List all tasks with ID, Title, Description, and Status
3. **Update Task**: Edit existing task's title or description
4. **Mark Complete**: Toggle task completion status
5. **Delete Task**: Remove a task permanently

## Development

- All code follows PEP 8 style guidelines with type hints
- Models are in `models.py` with proper data validation
- Business logic is in `store.py` with CRUD operations
- CLI interface is in `cli.py` with menu navigation
- Main entry point in `main.py` with Python version verification
- Tests in `tests/` directory using pytest

## Testing

Run the test suite:
```bash
pytest tests/
```

This will run all tests for the in-memory store logic and task models.