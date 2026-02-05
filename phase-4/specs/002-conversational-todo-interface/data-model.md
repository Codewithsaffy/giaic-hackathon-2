# Data Model: Conversational Todo Interface

## Entities

### Conversation
**Description**: Represents a user's ongoing dialogue with the AI assistant
- **id**: UUID (Primary Key)
- **user_id**: String (Foreign Key to user table)
- **title**: String (Generated from first message or user-defined)
- **created_at**: DateTime (Timestamp of creation)
- **updated_at**: DateTime (Timestamp of last activity)
- **is_active**: Boolean (Whether conversation is currently active)

**Relationships**:
- One-to-many with ChatMessage (one conversation has many messages)
- Belongs to User (one user has many conversations)

**Validation Rules**:
- user_id must exist in users table
- created_at must be in past
- title length between 1-200 characters

### ChatMessage
**Description**: Individual message in a conversation, containing user input or AI response
- **id**: UUID (Primary Key)
- **conversation_id**: UUID (Foreign Key to conversation)
- **role**: String (Either "user" or "assistant")
- **content**: Text (The actual message content)
- **timestamp**: DateTime (When the message was sent/received)
- **sequence_number**: Integer (Order of message in conversation)

**Relationships**:
- Belongs to Conversation (many messages belong to one conversation)

**Validation Rules**:
- role must be either "user" or "assistant"
- content must not be empty
- sequence_number must be positive integer
- timestamp must be in past

### TaskOperation
**Description**: Structured representation of a task action derived from natural language
- **id**: UUID (Primary Key)
- **conversation_id**: UUID (Foreign Key to conversation)
- **operation_type**: String (One of: "add_task", "list_tasks", "update_task", "complete_task", "delete_task")
- **raw_input**: Text (Original natural language input)
- **parsed_parameters**: JSON (Structured parameters extracted from input)
- **status**: String (One of: "pending", "processing", "completed", "failed")
- **result**: JSON (Result of the operation, if completed)
- **created_at**: DateTime (When operation was initiated)

**Relationships**:
- Belongs to Conversation (many operations belong to one conversation)

**Validation Rules**:
- operation_type must be one of allowed values
- status must be one of allowed values
- created_at must be in past
- parsed_parameters must be valid JSON

## State Transitions

### ChatMessage
- Created when user sends message or AI generates response
- Immutable after creation

### TaskOperation
- Created when natural language is parsed into operation
- Status transitions: pending → processing → completed/failed

## Indexes
- Conversation: user_id, created_at (for efficient user conversation retrieval)
- ChatMessage: conversation_id, sequence_number (for ordered message retrieval)
- TaskOperation: conversation_id, created_at (for operation history)