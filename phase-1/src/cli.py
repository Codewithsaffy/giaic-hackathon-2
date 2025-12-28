from typing import Optional
import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from datetime import datetime

try:
    from .store import task_store
    from .models import Task, Priority
    from .ui_components import (
        display_banner, display_dashboard, display_menu, create_task_table,
        display_task_card, display_success, display_error, display_warning,
        display_info, confirm_action
    )
    from .utils import parse_date, parse_tags, format_priority
except ImportError:
    from store import task_store
    from models import Task, Priority
    from ui_components import (
        display_banner, display_dashboard, display_menu, create_task_table,
        display_task_card, display_success, display_error, display_warning,
        display_info, confirm_action
    )
    from utils import parse_date, parse_tags, format_priority

# Create a console instance for rich output
console = Console()

# Create a Typer app instance
app = typer.Typer()


def add_task_interactive():
    """Add a new task with interactive prompts."""
    console.print("\n[bold cyan]➕ Create New Task[/bold cyan]\n")
    
    # Get title
    title = Prompt.ask("[bold]Task title[/bold]")
    if not title.strip():
        display_error("Title cannot be empty")
        return
    
    # Get description
    description = Prompt.ask("[bold]Description[/bold] (optional)", default="")
    
    # Get priority
    console.print("\n[bold]Priority:[/bold]")
    console.print("  [green]1.[/green] 🟢 Low")
    console.print("  [yellow]2.[/yellow] 🟡 Medium")
    console.print("  [red]3.[/red] 🔴 High")
    priority_choice = Prompt.ask("Select priority", choices=["1", "2", "3"], default="2")
    priority_map = {"1": Priority.LOW, "2": Priority.MEDIUM, "3": Priority.HIGH}
    priority = priority_map[priority_choice]
    
    # Get category
    categories = task_store.get_category_breakdown()
    if categories:
        console.print(f"\n[dim]Existing categories: {', '.join(categories.keys())}[/dim]")
    category = Prompt.ask("[bold]Category[/bold]", default="General")
    
    # Get due date
    console.print("\n[dim]Examples: 'tomorrow', 'next week', '2025-12-31', 'Dec 31'[/dim]")
    due_date_str = Prompt.ask("[bold]Due date[/bold] (optional)", default="none")
    due_date = parse_date(due_date_str)
    
    # Get tags
    tags_str = Prompt.ask("[bold]Tags[/bold] (comma-separated, optional)", default="")
    tags = parse_tags(tags_str)
    
    try:
        task = task_store.create_task(
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            category=category,
            tags=tags
        )
        display_success(f"Task created successfully! (ID: {task.id})")
        display_task_card(task)
    except ValueError as e:
        display_error(str(e))


def view_all_tasks():
    """Display all tasks in a table."""
    tasks = task_store.get_all_tasks()
    
    if not tasks:
        display_warning("No tasks found. Create your first task!")
        return
    
    console.print("\n")
    table = create_task_table(tasks, "All Tasks")
    console.print(table)
    console.print(f"\n[dim]Total: {len(tasks)} tasks[/dim]\n")


def show_dashboard():
    """Display interactive dashboard with statistics."""
    stats = task_store.get_completion_stats()
    priority_breakdown = task_store.get_priority_breakdown()
    category_breakdown = task_store.get_category_breakdown()
    overdue_tasks = task_store.get_overdue_tasks()
    
    console.print("\n")
    display_dashboard(stats, priority_breakdown, category_breakdown, len(overdue_tasks))
    
    # Show overdue tasks if any
    if overdue_tasks:
        console.print("\n")
        table = create_task_table(overdue_tasks, "⚠️  Overdue Tasks")
        console.print(table)
    
    # Show upcoming tasks
    upcoming = task_store.get_upcoming_tasks(7)
    if upcoming:
        console.print("\n")
        table = create_task_table(upcoming, "📅 Upcoming Tasks (Next 7 Days)")
        console.print(table)


def search_tasks_interactive():
    """Search tasks by keyword."""
    console.print("\n[bold cyan]🔍 Search Tasks[/bold cyan]\n")
    
    query = Prompt.ask("[bold]Search query[/bold]")
    
    if not query.strip():
        display_warning("Search query cannot be empty")
        return
    
    results = task_store.search_tasks(query)
    
    if not results:
        display_info(f"No tasks found matching '{query}'")
        return
    
    console.print("\n")
    table = create_task_table(results, f"Search Results for '{query}'")
    console.print(table)
    console.print(f"\n[dim]Found {len(results)} task(s)[/dim]\n")


def filter_tasks_interactive():
    """Filter tasks with interactive menu."""
    console.print("\n[bold cyan]🎯 Filter Tasks[/bold cyan]\n")
    console.print("Filter by:")
    console.print("  1. Priority")
    console.print("  2. Category")
    console.print("  3. Status (Completed/Pending)")
    console.print("  4. Overdue")
    
    choice = Prompt.ask("Select filter type", choices=["1", "2", "3", "4"])
    
    if choice == "1":
        # Filter by priority
        console.print("\n[bold]Priority:[/bold]")
        console.print("  1. 🟢 Low")
        console.print("  2. 🟡 Medium")
        console.print("  3. 🔴 High")
        priority_choice = Prompt.ask("Select priority", choices=["1", "2", "3"])
        priority_map = {"1": Priority.LOW, "2": Priority.MEDIUM, "3": Priority.HIGH}
        priority = priority_map[priority_choice]
        
        results = task_store.filter_by_priority(priority)
        title = f"Tasks with {priority.value.upper()} Priority"
        
    elif choice == "2":
        # Filter by category
        categories = task_store.get_category_breakdown()
        if not categories:
            display_warning("No categories available")
            return
        
        console.print(f"\nAvailable categories: {', '.join(categories.keys())}")
        category = Prompt.ask("[bold]Category[/bold]")
        
        results = task_store.filter_by_category(category)
        title = f"Tasks in '{category}' Category"
        
    elif choice == "3":
        # Filter by status
        status_choice = Prompt.ask("[bold]Show[/bold]", choices=["completed", "pending"])
        completed = status_choice == "completed"
        
        results = task_store.filter_by_status(completed)
        title = f"{'Completed' if completed else 'Pending'} Tasks"
        
    else:
        # Show overdue
        results = task_store.get_overdue_tasks()
        title = "⚠️  Overdue Tasks"
    
    if not results:
        display_info("No tasks match the selected filter")
        return
    
    console.print("\n")
    table = create_task_table(results, title)
    console.print(table)
    console.print(f"\n[dim]Found {len(results)} task(s)[/dim]\n")


def view_task_details():
    """View detailed information about a specific task."""
    console.print("\n[bold cyan]👁️  View Task Details[/bold cyan]\n")
    
    try:
        task_id = int(Prompt.ask("[bold]Task ID[/bold]"))
        task = task_store.get_task_by_id(task_id)
        console.print("\n")
        display_task_card(task)
    except ValueError as e:
        display_error(str(e))
    except Exception:
        display_error("Invalid task ID")


def update_task_interactive():
    """Update a task with interactive prompts."""
    console.print("\n[bold cyan]✏️  Update Task[/bold cyan]\n")
    
    try:
        task_id = int(Prompt.ask("[bold]Task ID to update[/bold]"))
        task = task_store.get_task_by_id(task_id)
        
        console.print("\n[dim]Current task details:[/dim]")
        display_task_card(task)
        
        console.print("\n[dim]Leave blank to keep current value[/dim]\n")
        
        # Update title
        new_title = Prompt.ask("[bold]New title[/bold]", default=task.title)
        
        # Update description
        new_description = Prompt.ask("[bold]New description[/bold]", default=task.description)
        
        # Update priority
        console.print("\n[bold]New priority:[/bold]")
        console.print("  1. 🟢 Low")
        console.print("  2. 🟡 Medium")
        console.print("  3. 🔴 High")
        current_priority_num = {"low": "1", "medium": "2", "high": "3"}[task.priority.value]
        priority_choice = Prompt.ask("Select priority", default=current_priority_num)
        priority_map = {"1": Priority.LOW, "2": Priority.MEDIUM, "3": Priority.HIGH}
        new_priority = priority_map[priority_choice]
        
        # Update category
        new_category = Prompt.ask("[bold]New category[/bold]", default=task.category)
        
        # Update due date
        current_due = task.due_date.strftime("%Y-%m-%d") if task.due_date else "none"
        due_date_str = Prompt.ask("[bold]New due date[/bold]", default=current_due)
        new_due_date = parse_date(due_date_str) if due_date_str != current_due else task.due_date
        
        # Update tags
        current_tags = ", ".join(task.tags) if task.tags else ""
        tags_str = Prompt.ask("[bold]New tags[/bold]", default=current_tags)
        new_tags = parse_tags(tags_str)
        
        task_store.update_task(
            task_id=task_id,
            title=new_title if new_title != task.title else None,
            description=new_description if new_description != task.description else None,
            priority=new_priority if new_priority != task.priority else None,
            due_date=new_due_date if due_date_str != current_due else None,
            category=new_category if new_category != task.category else None,
            tags=new_tags if tags_str != current_tags else None
        )
        
        display_success(f"Task {task_id} updated successfully!")
        
        updated_task = task_store.get_task_by_id(task_id)
        display_task_card(updated_task)
        
    except ValueError as e:
        display_error(str(e))
    except Exception as e:
        display_error(f"Error: {e}")


def toggle_task_status():
    """Toggle task completion status."""
    console.print("\n[bold cyan]✅ Toggle Task Status[/bold cyan]\n")
    
    try:
        task_id = int(Prompt.ask("[bold]Task ID[/bold]"))
        task = task_store.toggle_task_status(task_id)
        
        status = "completed" if task.status else "incomplete"
        display_success(f"Task {task_id} marked as {status}")
        display_task_card(task)
        
    except ValueError as e:
        display_error(str(e))
    except Exception:
        display_error("Invalid task ID")


def delete_task_interactive():
    """Delete a task with confirmation."""
    console.print("\n[bold cyan]🗑️  Delete Task[/bold cyan]\n")
    
    try:
        task_id = int(Prompt.ask("[bold]Task ID to delete[/bold]"))
        task = task_store.get_task_by_id(task_id)
        
        console.print("\n[dim]Task to delete:[/dim]")
        display_task_card(task)
        
        if confirm_action("Are you sure you want to delete this task?"):
            task_store.delete_task(task_id)
            display_success(f"Task {task_id} deleted successfully")
        else:
            display_info("Delete cancelled")
            
    except ValueError as e:
        display_error(str(e))
    except Exception:
        display_error("Invalid task ID")


def main_menu():
    """
    Display the main menu and handle user input.
    Enhanced with beautiful UI and new features.
    """
    # Show banner once at startup
    display_banner()
    
    while True:
        display_menu()
        
        choice = Prompt.ask("\n[bold magenta]Choose an option[/bold magenta]", choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])
        
        if choice == "1":
            add_task_interactive()
        elif choice == "2":
            view_all_tasks()
        elif choice == "3":
            show_dashboard()
        elif choice == "4":
            search_tasks_interactive()
        elif choice == "5":
            filter_tasks_interactive()
        elif choice == "6":
            view_task_details()
        elif choice == "7":
            update_task_interactive()
        elif choice == "8":
            toggle_task_status()
        elif choice == "9":
            delete_task_interactive()
        elif choice == "0":
            if confirm_action("Are you sure you want to exit?"):
                console.print("\n[bold cyan]👋 Goodbye! Stay productive! ✨[/bold cyan]\n")
                break
            else:
                continue


# Legacy Typer commands for backwards compatibility
@app.command()
def add(
    title: str = typer.Argument(..., help="Title of the task"),
    description: str = typer.Argument("", help="Description of the task"),
    priority: str = typer.Option("medium", help="Priority: low, medium, high"),
):
    """Add a new task."""
    try:
        priority_enum = Priority(priority.lower())
        task = task_store.create_task(title, description, priority=priority_enum)
        console.print(f"[green]✓ Task added successfully![/green]")
        console.print(f"ID: {task.id}, Title: {task.title}, Priority: {format_priority(task.priority.value)}")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")


@app.command()
def list():
    """List all tasks."""
    view_all_tasks()


@app.command()
def show(task_id: int = typer.Argument(..., help="ID of the task to show")):
    """Show details of a specific task."""
    try:
        task = task_store.get_task_by_id(task_id)
        display_task_card(task)
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")


@app.command()
def complete(task_id: int = typer.Argument(..., help="ID of the task to mark as complete")):
    """Mark a task as complete."""
    try:
        task = task_store.toggle_task_status(task_id)
        status = "complete" if task.status else "incomplete"
        console.print(f"[green]✓ Task {task.id} marked as {status}![/green]")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")


@app.command()
def delete(task_id: int = typer.Argument(..., help="ID of the task to delete")):
    """Delete a task."""
    try:
        result = task_store.delete_task(task_id)
        if result:
            console.print(f"[green]✓ Task {task_id} deleted![/green]")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")


@app.command()
def dashboard():
    """Show statistics dashboard."""
    show_dashboard()


@app.command()
def search(query: str = typer.Argument(..., help="Search query")):
    """Search tasks by keyword."""
    results = task_store.search_tasks(query)
    
    if not results:
        console.print(f"[yellow]No tasks found matching '{query}'[/yellow]")
        return
    
    table = create_task_table(results, f"Search Results for '{query}'")
    console.print(table)


if __name__ == "__main__":
    # If run directly, start the main menu
    main_menu()