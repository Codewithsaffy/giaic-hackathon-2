"""UI components for the enhanced CLI todo app."""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.progress import Progress, BarColumn, TextColumn
from rich import box
from rich.columns import Columns
from rich.text import Text
from pyfiglet import Figlet
from datetime import datetime

try:
    from .models import Task, Priority
    from .utils import format_date, format_priority, format_tags
except ImportError:
    from models import Task, Priority
    from utils import format_date, format_priority, format_tags

console = Console()


def display_banner():
    """Display beautiful ASCII art banner."""
    fig = Figlet(font='slant')
    banner_text = fig.renderText('TODO APP')
    
    console.print(Panel(
        f"[bold cyan]{banner_text}[/bold cyan]"
        f"\n[dim]✨ Your Advanced Task Management CLI ✨[/dim]",
        border_style="bright_cyan",
        box=box.DOUBLE
    ))


def display_dashboard(stats: dict, priority_breakdown: dict, category_breakdown: dict, overdue_count: int):
    """
    Display an interactive dashboard with statistics.
    
    Args:
        stats: Completion statistics dict
        priority_breakdown: Priority breakdown dict
        category_breakdown: Category breakdown dict
        overdue_count: Number of overdue tasks
    """
    console.print("\n")
    
    # Stats summary
    total = stats['total']
    completed = stats['completed']
    pending = stats['pending']
    percentage = stats['percentage']
    
    # Create progress bar
    if total > 0:
        with Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=40),
            TextColumn("[bold]{task.percentage:.1f}%"),
            console=console
        ) as progress:
            task = progress.add_task("Overall Progress", total=100, completed=percentage)
    
    # Stats grid
    stats_grid = Table.grid(padding=1)
    stats_grid.add_column(style="bold cyan", justify="center")
    stats_grid.add_column(style="bold yellow", justify="center")
    stats_grid.add_column(style="bold green", justify="center")
    stats_grid.add_column(style="bold magenta", justify="center")
    
    stats_grid.add_row(
        f"📊 Total\n[bold white]{total}[/bold white]",
        f"✅ Completed\n[bold white]{completed}[/bold white]",
        f"⏳ Pending\n[bold white]{pending}[/bold white]",
        f"⚠️  Overdue\n[bold white]{overdue_count}[/bold white]"
    )
    
    console.print(Panel(stats_grid, title="[bold]Task Statistics[/bold]", border_style="blue"))
    
    # Priority breakdown
    if total > 0:
        priority_table = Table(title="Priority Breakdown", box=box.SIMPLE)
        priority_table.add_column("Priority", style="bold")
        priority_table.add_column("Count", justify="right")
        priority_table.add_column("Percentage", justify="right")
        
        for priority_name, count in priority_breakdown.items():
            pct = (count / total * 100) if total > 0 else 0
            priority_table.add_row(
                format_priority(priority_name),
                str(count),
                f"{pct:.1f}%"
            )
        
        # Category breakdown
        category_table = Table(title="Category Breakdown", box=box.SIMPLE)
        category_table.add_column("Category", style="bold cyan")
        category_table.add_column("Count", justify="right")
        
        for category, count in sorted(category_breakdown.items(), key=lambda x: x[1], reverse=True)[:5]:
            category_table.add_row(category, str(count))
        
        # Display side by side
        console.print(Columns([priority_table, category_table], equal=True, expand=True))


def create_task_table(tasks: list, title: str = "Task List") -> Table:
    """
    Create a beautiful table for displaying tasks.
    
    Args:
        tasks: List of Task objects
        title: Table title
        
    Returns:
        Rich Table object
    """
    table = Table(title=title, box=box.ROUNDED, show_header=True, header_style="bold magenta")
    
    table.add_column("ID", style="dim", width=4, justify="center")
    table.add_column("Status", width=6, justify="center")
    table.add_column("Priority", width=15)
    table.add_column("Title", min_width=20, max_width=40)
    table.add_column("Category", width=12)
    table.add_column("Due Date", width=25)
    table.add_column("Tags", width=15)
    
    for task in tasks:
        # Status icon
        status = "✅" if task.status else "⬜"
        
        # Priority with color
        priority_display = format_priority(task.priority.value)
        
        # Title - strike through if completed
        title_display = f"[dim strikethrough]{task.title}[/dim strikethrough]" if task.status else task.title
        
        # Category
        category_display = f"[cyan]{task.category}[/cyan]"
        
        # Due date with formatting
        due_date_display = format_date(task.due_date)
        
        # Tags
        tags_display = format_tags(task.tags)
        
        table.add_row(
            str(task.id),
            status,
            priority_display,
            title_display,
            category_display,
            due_date_display,
            tags_display
        )
    
    return table


def display_task_card(task: Task):
    """
    Display detailed view of a single task in a beautiful card format.
    
    Args:
        task: Task object to display
    """
    # Status
    status_text = "✅ [green bold]COMPLETED[/green bold]" if task.status else "⬜ [yellow]PENDING[/yellow]"
    
    # Build card content
    card_content = f"""
[bold cyan]ID:[/bold cyan] {task.id}
[bold cyan]Status:[/bold cyan] {status_text}
[bold cyan]Priority:[/bold cyan] {format_priority(task.priority.value)}
[bold cyan]Category:[/bold cyan] [cyan]{task.category}[/cyan]

[bold cyan]Title:[/bold cyan]
{task.title}

[bold cyan]Description:[/bold cyan]
{task.description if task.description else '[dim]No description[/dim]'}

[bold cyan]Due Date:[/bold cyan] {format_date(task.due_date)}
[bold cyan]Tags:[/bold cyan] {format_tags(task.tags)}

[dim]Created: {task.created_at.strftime('%b %d, %Y %H:%M')}[/dim]
[dim]Updated: {task.updated_at.strftime('%b %d, %Y %H:%M')}[/dim]
    """.strip()
    
    # Show overdue warning if applicable
    if task.is_overdue():
        card_content = f"[red bold]⚠️  OVERDUE TASK ⚠️[/red bold]\n\n{card_content}"
    
    console.print(Panel(
        card_content,
        title=f"[bold]Task #{task.id}[/bold]",
        border_style="cyan" if not task.status else "green",
        box=box.DOUBLE
    ))


def display_menu():
    """Display the main menu with beautiful formatting."""
    menu_items = [
        ("1", "📝 Add Task", "Create a new task"),
        ("2", "📋 View All Tasks", "Display all tasks in a table"),
        ("3", "📊 Dashboard", "View statistics and analytics"),
        ("4", "🔍 Search Tasks", "Search tasks by keyword"),
        ("5", "🎯 Filter Tasks", "Filter by category, priority, or status"),
        ("6", "👁️  View Task Details", "Show detailed task information"),
        ("7", "✏️  Update Task", "Modify task properties"),
        ("8", "✅ Toggle Complete", "Mark task as complete/incomplete"),
        ("9", "🗑️  Delete Task", "Remove a task"),
        ("0", "🚪 Exit", "Exit the application"),
    ]
    
    table = Table(box=box.ROUNDED, show_header=False, padding=(0, 2))
    table.add_column("Option", style="bold cyan", width=8)
    table.add_column("Action", style="bold white", width=25)
    table.add_column("Description", style="dim", width=35)
    
    for option, action, description in menu_items:
        table.add_row(option, action, description)
    
    console.print("\n")
    console.print(Panel(table, title="[bold magenta]Main Menu[/bold magenta]", border_style="magenta"))


def display_success(message: str):
    """Display success message."""
    console.print(f"\n[green bold]✓ {message}[/green bold]\n")


def display_error(message: str):
    """Display error message."""
    console.print(f"\n[red bold]✗ {message}[/red bold]\n")


def display_warning(message: str):
    """Display warning message."""
    console.print(f"\n[yellow bold]⚠ {message}[/yellow bold]\n")


def display_info(message: str):
    """Display info message."""
    console.print(f"\n[blue]ℹ {message}[/blue]\n")


def confirm_action(prompt: str) -> bool:
    """
    Ask for confirmation before destructive actions.
    
    Args:
        prompt: Confirmation prompt
        
    Returns:
        True if user confirms, False otherwise
    """
    from rich.prompt import Confirm
    return Confirm.ask(f"\n[yellow]{prompt}[/yellow]")
