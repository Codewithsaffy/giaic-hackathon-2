from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class Priority(Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Task:
    """
    Represents a single todo item with enhanced attributes.

    Fields:
    - id: int - Unique identifier for the task (auto-generated)
    - title: str - Title of the task (required, non-empty)
    - description: str - Detailed description of the task (optional, can be empty)
    - status: bool - Completion status (False = incomplete [ ], True = complete [x])
    - priority: Priority - Task priority (LOW, MEDIUM, HIGH)
    - due_date: Optional[datetime] - Due date/deadline for the task
    - category: str - Category for organizing tasks (default: "General")
    - tags: List[str] - Tags for additional organization
    - created_at: datetime - Timestamp when task was created
    - updated_at: datetime - Timestamp when task was last updated
    """
    id: int
    title: str
    description: str = ""
    status: bool = False  # Defaults to False (incomplete) when creating a new task
    priority: Priority = Priority.MEDIUM
    due_date: Optional[datetime] = None
    category: str = "General"
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate the task after initialization."""
        if not self.title.strip():
            raise ValueError("Title must be provided and not empty")
        if not isinstance(self.id, int):
            raise TypeError("ID must be an integer")
        if not isinstance(self.status, bool):
            raise TypeError("Status must be a boolean")
        
        # Convert string priority to Priority enum if needed
        if isinstance(self.priority, str):
            try:
                self.priority = Priority(self.priority.lower())
            except ValueError:
                self.priority = Priority.MEDIUM
        
        # Convert string dates to datetime if needed
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)
        if isinstance(self.due_date, str):
            self.due_date = datetime.fromisoformat(self.due_date)

    def to_dict(self) -> dict:
        """Convert task to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority.value,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "category": self.category,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Create task from dictionary (for JSON deserialization)."""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            status=data.get("status", False),
            priority=data.get("priority", "medium"),
            due_date=data.get("due_date"),
            category=data.get("category", "General"),
            tags=data.get("tags", []),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat())
        )
    
    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if self.due_date is None or self.status:
            return False
        return datetime.now() > self.due_date
    
    def days_until_due(self) -> Optional[int]:
        """Calculate days until due date."""
        if self.due_date is None:
            return None
        delta = self.due_date - datetime.now()
        return delta.days