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
-   `priority` (Enum: "High", "Medium", "Low", default "Medium"): (New) Indicates the importance of the task.
-   `tags` (Array of Strings): (New) A list of descriptive labels for the task (e.g., "work", "personal", "urgent").
-   `due_date` (DateTime, Nullable): (New) The specific date and time by which the task should be completed.
-   `recurrence_pattern` (String, Nullable): (New) Defines how often the task should repeat (e.g., "daily", "weekly on Monday", "monthly on 15th"). This field will contain a serialized pattern that the Recurring Task Service interprets.
-   `reminder_settings` (JSON Object, Nullable): (New) Configuration for reminders.
    -   `time_offset` (String): e.g., "1 hour before", "1 day before", "at due time".
    -   `method` (Enum: "notification", "email"): Preferred reminder delivery method.
-   `external_id` (String, Nullable): Optional, for integration with external systems if needed.

**Relationships**:

-   One-to-many with `Notification` (a Task can have multiple Notifications, though a Notification might also be generic).

### Notification

Represents a message to be sent to a user, typically for reminders or system updates.

**Attributes**:

-   `id` (UUID): Primary key, unique identifier for the notification.
-   `user_id` (UUID): Foreign key, links to the recipient user.
-   `task_id` (UUID, Nullable): Foreign key, links to the associated task (if applicable).
-   `message` (String): The content of the notification.
-   `trigger_time` (DateTime): The scheduled date and time when the notification should be sent.
-   `sent_at` (DateTime, Nullable): Timestamp when the notification was actually sent.
-   `status` (Enum: "pending", "sent", "failed", "cancelled"): Current state of the notification.
-   `type` (Enum: "reminder", "system_alert", "info"): Type of notification.

**Relationships**:

-   Many-to-one with `Task` (a Notification can be for a specific Task).
-   Many-to-one with `User` (a Notification belongs to a User).

### Event

Represents a significant occurrence or state change within the system, used for inter-service communication via Kafka.

**Attributes**:

-   `id` (UUID): Primary key, unique identifier for the event.
-   `type` (String): Describes the type of event (e.g., "task_created", "task_updated", "reminder_triggered", "recurring_task_instance_created").
-   `payload` (JSON Object): Contains the relevant data for the event, structured according to the `type`.
    -   For `task_created`: full `Task` object.
    -   For `task_updated`: `Task` ID and updated fields.
    -   For `reminder_triggered`: `Notification` object, `Task` ID, `user_id`.
    -   For `recurring_task_instance_created`: new `Task` object.
-   `source_service` (String): The microservice that originated the event.
-   `timestamp` (DateTime): The exact time the event occurred.
-   `version` (Integer): Schema version of the event payload.

**Relationships**:

-   None directly modeled, but implicitly linked to `Task` and `Notification` via `payload` content.

## Relationships Overview

-   A `User` can have many `Tasks`.
-   A `Task` can have associated `Notifications`.
-   `Events` facilitate communication between services, often carrying data about `Tasks` or triggering `Notifications`.
