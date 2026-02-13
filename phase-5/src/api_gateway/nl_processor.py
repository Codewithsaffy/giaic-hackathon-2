import re
from typing import Optional, Tuple, List
from uuid import UUID
from datetime import datetime, timedelta # Import datetime, timedelta

from src.shared.models import Priority


class NLProcessor:
    def __init__(self):
        pass

    def process_command(self, text: str) -> Optional[Tuple[str, dict]]:
        """
        Processes a natural language command and extracts intent and entities.
        Returns a tuple of (intent, params) or None if no intent is recognized.
        """
        text = text.lower().strip()

        # Set Priority command
        priority_match = re.match(r"set priority of task (\S+) to (high|medium|low)", text)
        if priority_match:
            task_id_str = priority_match.group(1)
            priority_str = priority_match.group(2)
            try:
                task_id = UUID(task_id_str)
                priority = Priority(priority_str.capitalize())
                return "set_task_priority", {"task_id": task_id, "priority": priority}
            except ValueError:
                return None # Invalid UUID or priority value

        # Add Tags command
        add_tags_match = re.match(r"add tags (.+) to task (\S+)", text)
        if add_tags_match:
            tags_str = add_tags_match.group(1)
            task_id_str = add_tags_match.group(2)
            try:
                task_id = UUID(task_id_str)
                tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
                return "add_task_tags", {"task_id": task_id, "tags": tags}
            except ValueError:
                return None # Invalid UUID

        # Remove Tags command
        remove_tags_match = re.match(r"remove tags (.+) from task (\S+)", text)
        if remove_tags_match:
            tags_str = remove_tags_match.group(1)
            task_id_str = remove_tags_match.group(2)
            try:
                task_id = UUID(task_id_str)
                tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
                return "remove_task_tags", {"task_id": task_id, "tags": tags}
            except ValueError:
                return None # Invalid UUID

        # Get Tasks by Tag command
        get_by_tag_match = re.match(r"show tasks tagged (.+)", text)
        if get_by_tag_match:
            tag = get_by_tag_match.group(1).strip()
            return "get_tasks_by_tag", {"tag_name": tag}

        # Search, Filter, Sort command
        search_filter_sort_match = re.match(
            r"(find task|show tasks)(?: containing '(.+?)')?(?: with priority (high|medium|low))?(?: tagged (.+?))?(?: sorted by (created_at|due_date|priority)(?: (asc|desc))?)?",
            text
        )
        if search_filter_sort_match:
            query = search_filter_sort_match.group(2)
            priority_str = search_filter_sort_match.group(3)
            tags_str = search_filter_sort_match.group(4)
            sort_by = search_filter_sort_match.group(5)
            sort_order = search_filter_sort_match.group(6)

            params = {}
            if query:
                params["query"] = query
            if priority_str:
                params["priority"] = Priority(priority_str.capitalize())
            if tags_str:
                params["tags"] = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
            if sort_by:
                params["sort_by"] = sort_by
            if sort_order:
                params["sort_order"] = sort_order

            return "search_filter_sort_tasks", params

        # Create Recurring Task command
        create_recurring_task_match = re.match(r"create a task '(.+)' every (.+)", text)
        if create_recurring_task_match:
            description = create_recurring_task_match.group(1)
            recurrence_pattern = create_recurring_task_match.group(2)
            return "create_recurring_task", {"description": description, "recurrence_pattern": recurrence_pattern}

        # Set Due Date and Reminder command
        set_due_reminder_match = re.match(r"set due date for task (\S+) to (.+) and remind me (.+)", text)
        if set_due_reminder_match:
            task_id_str = set_due_reminder_match.group(1)
            due_date_str = set_due_reminder_match.group(2)
            reminder_offset_str = set_due_reminder_match.group(3)
            try:
                task_id = UUID(task_id_str)
                # This is a simplification; full date parsing is complex.
                # Assuming "tomorrow 5 PM" implies datetime.now() + timedelta + time parse
                # For now, just pass the string to the service for more robust parsing.
                # A proper NL to datetime parser would be needed.
                
                # Placeholder: Convert simple "tomorrow X PM" to a basic datetime object for now
                if "tomorrow" in due_date_str:
                    today = datetime.now()
                    due_date = today + timedelta(days=1)
                    due_date = due_date.replace(hour=17, minute=0, second=0, microsecond=0)
                elif "in" in due_date_str and "minute" in due_date_str:
                    minutes_match = re.search(r"(\d+)", due_date_str)
                    if minutes_match:
                        minutes = int(minutes_match.group(1))
                        due_date = datetime.now() + timedelta(minutes=minutes)
                    else:
                        due_date = datetime.now() + timedelta(days=2)
                else:
                    due_date = datetime.now() + timedelta(days=2)


                return "set_task_due_reminder", {
                    "task_id": task_id,
                    "due_date": due_date.isoformat(), # Pass ISO formatted string
                    "reminder_offset": reminder_offset_str
                }
            except ValueError:
                return None # Invalid UUID

        # Create Task command
        create_task_match = re.search(r"(add|create) (?:a )?(?:.+ )?task ['\"]?(.+?)['\"]?(?: with priority (high|medium|low))?(?: tagged (.+))?", text)
        if create_task_match:
            description = create_task_match.group(2)
            priority_str = create_task_match.group(3)
            tags_str = create_task_match.group(4)
            
            params = {"description": description}
            if priority_str:
                params["priority"] = Priority(priority_str.capitalize())
            if tags_str:
                params["tags"] = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
            
            return "create_task", params

        return None # No matching command
