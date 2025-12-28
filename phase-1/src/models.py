from dataclasses import dataclass
from typing import Optional


@dataclass
class Task:
    """
    Represents a single todo item with ID, Title, Description, and Status attributes.

    Fields:
    - id: int - Unique identifier for the task (auto-generated)
    - title: str - Title of the task (required, non-empty)
    - description: str - Detailed description of the task (optional, can be empty)
    - status: bool - Completion status (False = incomplete [ ], True = complete [x])
    """
    id: int
    title: str
    description: str
    status: bool = False  # Defaults to False (incomplete) when creating a new task

    def __post_init__(self):
        """Validate the task after initialization."""
        if not self.title.strip():
            raise ValueError("Title must be provided and not empty")
        if not isinstance(self.id, int):
            raise TypeError("ID must be an integer")
        if not isinstance(self.status, bool):
            raise TypeError("Status must be a boolean")