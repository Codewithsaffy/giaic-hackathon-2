# Data Model: Intermediate & Advanced Todo Chatbot Features

This document outlines the key entities and their attributes for the Intermediate and Advanced features of the Todo Chatbot. The model is designed to support priorities, tags, recurring tasks, due dates, reminders, and event-driven operations.

## Entities

### Task

Represents a user's task within the system.

**Attributes**:

-   `id` (UUID): Primary key, unique identifier for the task.
-   `user_id` (UUID): Foreign key, links to the user who owns the task.
-   `description` (String): The main content or description of the task.
-   `status` (Enum: "pending", "completed", "archived"): Current state of the task.
-   `created_at` (DateTime): Timestamp when the task was created.
-   `updated_at` (DateTime): Timestamp of the last update to the task.
-   `priority` (Integer, default 3): (New) Indicates the importance of the task (1=High, 2=Medium, 3=Low).
-   `tags` (String, Nullable): (New) Comma-separated labels for the task (e.g., "work,urgent").
-   `due_date` (DateTime, Nullable): (New) The specific date and time for task completion.
-   `remind_at` (DateTime, Nullable): (New) Exact timestamp for the reminder trigger via Dapr Jobs API.
-   `recurring_interval` (String, Nullable): (New) Defines repetition (e.g., "daily", "weekly").
-   `completed` (Boolean, default False): (Existing) Current state of the task.
-   `user_id` (String): (Existing) Foreign key to user.

**Relationships**:

-   One-to-many with `Notification` (triggered via Pub/Sub).

### Notification

Represents a generic message delivery handled by the `notification-service`.

**Attributes**:

-   `id` (UUID): Primary key.
-   `user_id` (String): Recipient.
-   `task_id` (Integer, Nullable): Associated task.
-   `message` (String): Content.
-   `status` (Enum: "pending", "sent", "failed"): State of delivery.

### Event

Represents a state change within the system, used for inter-service communication via Redis Pub/Sub.

**Attributes**:

-   `id` (UUID): Primary key.
-   `type` (String): (e.g., "task_created", "task_updated").
-   `payload` (JSON Object): Contains the relevant data for the event.
-   `timestamp` (DateTime): The exact time the event occurred.

**Relationships**:

-   None directly modeled, but implicitly linked to `Task` and `Notification` via `payload` content.

## Relationships Overview

-   A `User` can have many `Tasks`.
-   A `Task` can have associated `Notifications`.
-   `Events` facilitate communication between services, often carrying data about `Tasks` or triggering `Notifications`.
