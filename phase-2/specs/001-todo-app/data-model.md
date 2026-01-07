# Data Model: Todo App

## Entity Definitions

### User
**Description**: Represents an authenticated user in the system
**Fields**:
- `id`: UUID (Primary Key) - Unique identifier for the user
- `email`: String (Unique) - User's email address for authentication
- `password_hash`: String - Securely hashed password
- `name`: String - User's display name
- `created_at`: DateTime - Timestamp when user account was created
- `updated_at`: DateTime - Timestamp when user account was last updated
- `is_active`: Boolean - Whether the account is active (default: true)

**Validation Rules**:
- Email must be a valid email format
- Email must be unique across all users
- Password must meet security requirements (min 8 chars, etc.)
- Name must be 1-100 characters

**Relationships**:
- One-to-Many with Task (user has many tasks)

### Task
**Description**: Represents a user's personal task in the todo list
**Fields**:
- `id`: UUID (Primary Key) - Unique identifier for the task
- `title`: String - Task title/description (required)
- `description`: String (Optional) - Detailed description of the task
- `completed`: Boolean - Whether the task is completed (default: false)
- `created_at`: DateTime - Timestamp when task was created
- `updated_at`: DateTime - Timestamp when task was last updated
- `owner_id`: UUID (Foreign Key) - Reference to the owning user

**Validation Rules**:
- Title must be 1-200 characters
- Description can be up to 500 characters if provided
- Owner ID must reference an existing user
- Only the owner can modify the task

**Relationships**:
- Many-to-One with User (task belongs to one user)

## State Transitions

### Task State Transitions
- **Created**: Task is initially created with `completed = false`
- **Completed**: Task status changes to `completed = true` when marked complete
- **Reopened**: Task status changes back to `completed = false` if needed
- **Deleted**: Task is removed from the system (soft delete with `deleted_at` field)

## Database Schema

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    owner_id UUID NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_tasks_owner_id ON tasks(owner_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_users_email ON users(email);
```

## API Data Contracts

### User Registration Input
```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "name": "John Doe"
}
```

### User Response
```json
{
  "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2026-01-06T10:00:00Z"
}
```

### Task Creation Input
```json
{
  "title": "Buy groceries",
  "description": "Milk, bread, eggs",
  "completed": false
}
```

### Task Response
```json
{
  "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "title": "Buy groceries",
  "description": "Milk, bread, eggs",
  "completed": false,
  "created_at": "2026-01-06T10:00:00Z",
  "updated_at": "2026-01-06T10:00:00Z",
  "owner_id": "f0e9d8c7-b6a5-4321-fedc-ba9876543210"
}
```

## Validation Rules Summary

### User Validation
- Email format validation using standard regex
- Password strength: minimum 8 characters with uppercase, lowercase, number
- Name: 1-100 characters, no special characters
- Unique email constraint enforced at database level

### Task Validation
- Title: 1-200 characters
- Description: 0-500 characters (optional)
- Only the task owner can modify/delete the task
- Creation date is automatically set by the system
- Update date is automatically updated on modifications