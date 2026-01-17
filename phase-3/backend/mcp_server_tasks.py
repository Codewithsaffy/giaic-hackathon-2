"""
MCP Server for Task Management
Exposes task CRUD operations as MCP tools for use with AI agents.
Fixed version with proper imports and structure.
"""
import logging
import sys
import os
from typing import Optional
from mcp.server.fastmcp import FastMCP

# Pre-import database to initialize engine early
try:
    from database import AsyncSessionFactory
    from models import TaskCreate, TaskUpdate
    import crud
    DATABASE_READY = True
except Exception as e:
    DATABASE_READY = False
    DATABASE_ERROR = str(e)

# Configure logging to stderr ONLY (Vercel has read-only filesystem)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("TaskManager")


@mcp.tool()
async def add_task(user_id: str, title: str, description: Optional[str] = None) -> str:
    """Add a new task for a user.
    
    Args:
        user_id: The ID of the user
        title: The task title
        description: Optional task description
        
    Returns:
        Success message with task ID or error message
    """
    logger.info(f"TOOL_START: add_task(user_id={user_id}, title={title})")
    if not DATABASE_READY:
        return f"Database error: {DATABASE_ERROR}"
        
    try:
        logger.info("ACTION: Opening database session...")
        async with AsyncSessionFactory() as session:
            logger.info("STATUS: Database session opened.")
            task_data = TaskCreate(title=title, description=description)
            logger.info("ACTION: Executing crud.create_task...")
            task = await crud.create_task(session, task_data, user_id)
            logger.info(f"STATUS: Task created with ID {task.id}")
            return f"Task created successfully with ID: {task.id}"
    except Exception as e:
        logger.error(f"ERROR: in add_task: {e}", exc_info=True)
        return f"Error creating task: {str(e)}"


@mcp.tool()
async def list_tasks(user_id: str, status: Optional[str] = None) -> str:
    """List all tasks for a user.
    
    Args:
        user_id: The ID of the user
        status: Optional filter - 'completed' or 'active'
        
    Returns:
        Formatted list of tasks or error message
    """
    logger.info(f"TOOL_START: list_tasks(user_id={user_id}, status={status})")
    if not DATABASE_READY:
        return f"Database error: {DATABASE_ERROR}"

    try:
        logger.info("ACTION: Opening database session...")
        async with AsyncSessionFactory() as session:
            logger.info("STATUS: Database session opened.")
            logger.info(f"ACTION: Executing crud.get_tasks_by_user for {user_id}...")
            tasks = await crud.get_tasks_by_user(session, user_id)
            
            # Filter by status if specified
            if status == "completed":
                tasks = [t for t in tasks if t.completed]
            elif status == "active":
                tasks = [t for t in tasks if not t.completed]
            
            if not tasks:
                logger.info("STATUS: No tasks found for user.")
                return "No tasks found."
            
            output = []
            for t in tasks:
                status_icon = "[x]" if t.completed else "[ ]"
                desc = f" - {t.description}" if t.description else ""
                output.append(f"{t.id}. {status_icon} **{t.title}**{desc}")
            
            logger.info(f"STATUS: Returning {len(tasks)} tasks.")
            return "\n".join(output)
    except Exception as e:
        logger.error(f"ERROR: in list_tasks: {e}", exc_info=True)
        return f"Error listing tasks: {str(e)}"


@mcp.tool()
async def complete_task(user_id: str, task_id: int) -> str:
    """Mark a task as completed.
    
    Args:
        user_id: The ID of the user
        task_id: The ID of the task to complete
        
    Returns:
        Success message or error message
    """
    logger.info(f"TOOL_START: complete_task(user_id={user_id}, task_id={task_id})")
    if not DATABASE_READY:
        return f"Database error: {DATABASE_ERROR}"

    try:
        async with AsyncSessionFactory() as session:
            task = await crud.get_task_by_id(session, task_id, user_id)
            if not task:
                return f"Task {task_id} not found or access denied."
            
            update_data = TaskUpdate(completed=True)
            await crud.update_task(session, task_id, update_data, user_id)
            return f"Task {task_id} marked as completed."
    except Exception as e:
        logger.error(f"ERROR: in complete_task: {e}", exc_info=True)
        return f"Error completing task: {str(e)}"


@mcp.tool()
async def delete_task(user_id: str, task_id: int) -> str:
    """Delete a task.
    
    Args:
        user_id: The ID of the user
        task_id: The ID of the task to delete
        
    Returns:
        Success message or error message
    """
    logger.info(f"TOOL_START: delete_task(user_id={user_id}, task_id={task_id})")
    if not DATABASE_READY:
        return f"Database error: {DATABASE_ERROR}"

    try:
        async with AsyncSessionFactory() as session:
            success = await crud.delete_task(session, task_id, user_id)
            if not success:
                return f"Task {task_id} not found or access denied."
            return f"Task {task_id} deleted successfully."
    except Exception as e:
        logger.error(f"ERROR: in delete_task: {e}", exc_info=True)
        return f"Error deleting task: {str(e)}"


@mcp.tool()
async def update_task(
    user_id: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> str:
    """Update a task's title or description.
    
    Args:
        user_id: The ID of the user
        task_id: The ID of the task to update
        title: New title (optional)
        description: New description (optional)
        
    Returns:
        Success message or error message
    """
    logger.info(f"TOOL_START: update_task(user_id={user_id}, task_id={task_id})")
    if not DATABASE_READY:
        return f"Database error: {DATABASE_ERROR}"

    try:
        async with AsyncSessionFactory() as session:
            task = await crud.get_task_by_id(session, task_id, user_id)
            if not task:
                return f"Task {task_id} not found or access denied."
            
            update_data = TaskUpdate(title=title, description=description)
            await crud.update_task(session, task_id, update_data, user_id)
            return f"Task {task_id} updated successfully."
    except Exception as e:
        logger.error(f"ERROR: in update_task: {e}", exc_info=True)
        return f"Error updating task: {str(e)}"


def main():
    """Run the MCP server with STDIO transport."""
    logger.info("Server initialization starting...")
    # Use stdio transport for local development
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()