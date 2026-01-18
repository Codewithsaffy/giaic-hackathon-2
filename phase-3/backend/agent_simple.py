"""
Unified Task Management Agent - Production Version
Integrates with TaskManager MCP server using Cerebras LLM.
"""
import asyncio
import os
import logging
import sys
from pathlib import Path
from agents import Agent, Runner, OpenAIChatCompletionsModel, set_tracing_disabled
from agents.mcp import MCPServerStdio
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger(__name__)

# Robustly load .env
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Configuration
api_key = os.getenv("CEREBRAS_API_KEY")
if not api_key:
    logger.error("CEREBRAS_API_KEY not found!")
    raise ValueError("CEREBRAS_API_KEY must be set in backend/.env")

set_tracing_disabled(True)

# Initialize Cerebras client
client = AsyncOpenAI(
    api_key=api_key,
    base_url="https://api.cerebras.ai/v1"
)

# Using Cerebras high-performance model
model = OpenAIChatCompletionsModel(
    model="qwen-3-32b", 
    openai_client=client
)

async def initialize_database():
    """Pre-initialize database tables."""
    try:
        from database import init_db
        logger.info("Initializing database via agent...")
        await init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.warning(f"Database initialization warning: {e}")

async def run_task_agent(user_id: str, message: str, mcp_server=None) -> str:
    """
    Core function to run the agent with MCP integration.
    Can reuse an existing mcp_server connection for persistent sessions.
    """
    try:
        # Define agent lifecycle handler
        async def execute_with_mcp(server):
            agent = Agent(
                name="TaskAssistant",
                instructions=f"""You are a helpful task management assistant for user_id: {user_id}.
                
                CRITICAL RULES:
                1. You are assisting user_id: "{user_id}"
                2. EVERY tool call to TaskManager MUST include user_id="{user_id}"
                3. Never ask for user_id - you already have it.
                4. Always format task lists as clean Markdown tables or lists.
                5. Acknowledge successful actions (Add/Complete/Delete).
                """,
                mcp_servers=[server],
                model=model
            )
            result = await Runner.run(agent, message)
            return str(result.final_output)

        if mcp_server:
            return await execute_with_mcp(mcp_server)
        else:
            # Fallback to one-off connection with robust timeout
            current_dir = os.path.dirname(os.path.abspath(__file__))
            mcp_server_path = os.path.join(current_dir, "mcp_server_tasks.py")
            logger.info(f"Starting MCP server with executable: {sys.executable}")
            logger.info(f"MCP server path: {mcp_server_path}")
            logger.info(f"Current working directory: {os.getcwd()}")
            
            async with MCPServerStdio(
                name="TaskManager",
                params={
                    "command": sys.executable,
                    "args": ["-u", mcp_server_path],
                    "env": os.environ.copy()
                },
                client_session_timeout_seconds=120
            ) as single_mcp:
                return await execute_with_mcp(single_mcp)

    except Exception as e:
        logger.error(f"Error in agent execution: {e}", exc_info=True)
        return f"Error: {str(e)}"

# Keep a simpler reference if needed for other modules
agent_runner = run_task_agent
