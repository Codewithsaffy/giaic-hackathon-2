from typing import Optional
import typer
from rich.console import Console
from rich.table import Table

try:
    from .store import task_store
    from .models import Task
except ImportError:
    from store import task_store
    from models import Task

# Create a console instance for rich output
console = Console()

# Create a Typer app instance
app = typer.Typer()


def add_task(title: str, description: str = "") -> Task:
    """
    Add a new task with the given title and description.

    Args:
        title (str): The title of the task
        description (str): The description of the task (optional)

    Returns:
        Task: The created Task object
    """
    try:
        task = task_store.create_task(title, description)
        console.print(f"[green]✓ Task added successfully![/green]")
        console.print(f"ID: {task.id}, Title: {task.title}")
        return task
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise


def view_tasks() -> None:
    """
    Display all tasks in a formatted table.
    Shows ID, Title, Description, and Status ([ ] or [x]) for each task.
    """
    tasks = task_store.get_all_tasks()

    if not tasks:
        console.print("[yellow]No tasks found.[/yellow]")
        return

    table = Table(title="Task List")
    table.add_column("ID", style="dim", width=5)
    table.add_column("Status", style="dim", width=8)
    table.add_column("Title", min_width=15)
    table.add_column("Description", min_width=20)

    for task in tasks:
        status = "[x]" if task.status else "[ ]"
        status_style = "green" if task.status else "red"
        table.add_row(
            str(task.id),
            f"[{status_style}]{status}[/{status_style}]",
            task.title,
            task.description
        )

    console.print(table)


@app.command()
def add(title: str = typer.Argument(..., help="Title of the task"),
        description: str = typer.Argument("", help="Description of the task")):
    """
    Add a new task with the given title and description.
    """
    add_task(title, description)


@app.command()
def list():
    """
    List all tasks with ID, Title, Description, and Status.
    """
    view_tasks()


@app.command()
def show(task_id: int = typer.Argument(..., help="ID of the task to show")):
    """
    Show details of a specific task by ID.
    """
    try:
        task = task_store.get_task_by_id(task_id)
        status = "[x]" if task.status else "[ ]"
        status_color = "green" if task.status else "red"

        console.print(f"ID: {task.id}")
        console.print(f"Status: [{status_color}]{status}[/{status_color}]")
        console.print(f"Title: {task.title}")
        console.print(f"Description: {task.description}")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")


@app.command()
def complete(task_id: int = typer.Argument(..., help="ID of the task to mark as complete")):
    """
    Mark a task as complete by ID.
    """
    try:
        task = task_store.toggle_task_status(task_id)
        status = "[x]" if task.status else "[ ]"
        console.print(f"[green]✓ Task {task.id} marked as {'complete' if task.status else 'incomplete'}![/green]")
        console.print(f"Status: {status} Title: {task.title}")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")


@app.command()
def update(
    task_id: int = typer.Argument(..., help="ID of the task to update"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="New title for the task"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="New description for the task")
):
    """
    Update a task's title or description by ID.
    """
    try:
        task = task_store.update_task(task_id, title, description)
        console.print(f"[green]✓ Task {task.id} updated![/green]")
        console.print(f"Title: {task.title}")
        if description is not None:
            console.print(f"Description: {task.description}")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")


@app.command()
def delete(task_id: int = typer.Argument(..., help="ID of the task to delete")):
    """
    Delete a task by ID.
    """
    try:
        result = task_store.delete_task(task_id)
        if result:
            console.print(f"[green]✓ Task {task_id} deleted![/green]")
        else:
            console.print(f"[red]Task with ID {task_id} not found.[/red]")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")


def main_menu():
    """
    Display the main menu and handle user input.
    Provides options for all task operations.
    """
    while True:
        console.print("\n[bold]CLI Todo Application[/bold]")
        console.print("1. Add Task")
        console.print("2. View Tasks")
        console.print("3. Update Task")
        console.print("4. Mark Complete/Incomplete")
        console.print("5. Delete Task")
        console.print("6. Exit")

        choice = typer.prompt("Choose an option (1-6)")

        if choice == "1":
            title = typer.prompt("Enter task title")
            description = typer.prompt("Enter task description (optional)", default="")
            add_task(title, description)
        elif choice == "2":
            view_tasks()
        elif choice == "3":
            try:
                task_id = int(typer.prompt("Enter task ID to update"))
                task = task_store.get_task_by_id(task_id)
                console.print(f"Current task: {task.title}")

                new_title = typer.prompt(f"Enter new title (current: {task.title})", default=task.title)
                new_description = typer.prompt(f"Enter new description (current: {task.description})", default=task.description)

                task_store.update_task(task_id, new_title, new_description)
                console.print(f"[green]✓ Task {task_id} updated![/green]")
            except ValueError as e:
                console.print(f"[red]Error: {e}[/red]")
        elif choice == "4":
            try:
                task_id = int(typer.prompt("Enter task ID to toggle status"))
                task = task_store.toggle_task_status(task_id)
                status = "complete" if task.status else "incomplete"
                console.print(f"[green]✓ Task {task_id} marked as {status}![/green]")
            except ValueError as e:
                console.print(f"[red]Error: {e}[/red]")
        elif choice == "5":
            try:
                task_id = int(typer.prompt("Enter task ID to delete"))
                result = task_store.delete_task(task_id)
                if result:
                    console.print(f"[green]✓ Task {task_id} deleted![/green]")
            except ValueError as e:
                console.print(f"[red]Error: {e}[/red]")
        elif choice == "6":
            console.print("[blue]Goodbye![/blue]")
            break
        else:
            console.print("[red]Invalid option. Please choose 1-6.[/red]")


if __name__ == "__main__":
    # If run directly, start the main menu
    main_menu()