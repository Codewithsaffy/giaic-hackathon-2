"""Utility functions for the CLI todo app."""
from datetime import datetime, timedelta
from typing import Optional
from dateutil import parser
from rich.console import Console

console = Console()


def parse_date(date_str: str) -> Optional[datetime]:
    """
    Parse a date string into a datetime object.
    Supports various formats: 'tomorrow', 'next week', '2025-12-31', 'Dec 31', etc.
    
    Args:
        date_str: Date string to parse
        
    Returns:
        datetime object or None if parsing fails
    """
    if not date_str or date_str.strip().lower() == "none":
        return None
    
    date_str = date_str.strip().lower()
    
    # Handle relative dates
    if date_str == "today":
        return datetime.now().replace(hour=23, minute=59, second=59)
    elif date_str == "tomorrow":
        return (datetime.now() + timedelta(days=1)).replace(hour=23, minute=59, second=59)
    elif date_str == "next week":
        return (datetime.now() + timedelta(weeks=1)).replace(hour=23, minute=59, second=59)
    elif date_str == "next month":
        return (datetime.now() + timedelta(days=30)).replace(hour=23, minute=59, second=59)
    
    # Try to parse with dateutil
    try:
        parsed_date = parser.parse(date_str, fuzzy=True)
        # If no time specified, set to end of day
        if parsed_date.hour == 0 and parsed_date.minute == 0:
            parsed_date = parsed_date.replace(hour=23, minute=59, second=59)
        return parsed_date
    except (parser.ParserError, ValueError):
        console.print(f"[yellow]Could not parse date: {date_str}[/yellow]")
        return None


def format_date(date: Optional[datetime]) -> str:
    """
    Format a datetime object for display.
    
    Args:
        date: datetime object to format
        
    Returns:
        Formatted date string
    """
    if date is None:
        return "No due date"
    
    now = datetime.now()
    delta = date - now
    days = delta.days
    
    # Color code based on urgency
    if days < 0:
        return f"[red bold]⚠️  {date.strftime('%b %d, %Y')} (OVERDUE)[/red bold]"
    elif days == 0:
        return f"[bright_red]🔥 {date.strftime('%b %d, %Y')} (TODAY!)[/bright_red]"
    elif days == 1:
        return f"[yellow]⚡ {date.strftime('%b %d, %Y')} (Tomorrow)[/yellow]"
    elif days <= 7:
        return f"[bright_yellow]📅 {date.strftime('%b %d, %Y')} (in {days} days)[/bright_yellow]"
    else:
        return f"[dim]📅 {date.strftime('%b %d, %Y')}[/dim]"


def format_priority(priority_str: str) -> str:
    """
    Format priority with color and icon.
    
    Args:
        priority_str: Priority value string
        
    Returns:
        Formatted priority string with colors and emojis
    """
    priority_str = priority_str.lower()
    
    if priority_str == "high":
        return "[red bold]🔴 HIGH[/red bold]"
    elif priority_str == "medium":
        return "[yellow]🟡 MEDIUM[/yellow]"
    else:  # low
        return "[green]🟢 LOW[/green]"


def validate_input(prompt: str, validator=None, default=None) -> str:
    """
    Validate user input with custom validator function.
    
    Args:
        prompt: Prompt to display
        validator: Optional validation function
        default: Default value if empty input
        
    Returns:
        Validated input string
    """
    from rich.prompt import Prompt
    
    while True:
        value = Prompt.ask(prompt, default=default if default else "")
        
        if not value and default:
            return default
        
        if validator is None:
            return value
        
        try:
            if validator(value):
                return value
            else:
                console.print("[red]Invalid input. Please try again.[/red]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


def get_completion_percentage(completed: int, total: int) -> float:
    """
    Calculate completion percentage.
    
    Args:
        completed: Number of completed tasks
        total: Total number of tasks
        
    Returns:
        Completion percentage (0-100)
    """
    if total == 0:
        return 0.0
    return (completed / total) * 100


def parse_tags(tags_str: str) -> list[str]:
    """
    Parse comma-separated tags string into list.
    
    Args:
        tags_str: Comma-separated tags string
        
    Returns:
        List of tag strings
    """
    if not tags_str or tags_str.strip().lower() == "none":
        return []
    
    return [tag.strip() for tag in tags_str.split(",") if tag.strip()]


def format_tags(tags: list[str]) -> str:
    """
    Format tags for display.
    
    Args:
        tags: List of tag strings
        
    Returns:
        Formatted tags string
    """
    if not tags:
        return "[dim]-[/dim]"
    
    return " ".join([f"[cyan]#{tag}[/cyan]" for tag in tags])
