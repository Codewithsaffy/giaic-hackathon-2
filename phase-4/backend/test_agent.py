import asyncio
import logging
import sys
import os

# Set up logging to stdout
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

from agent_simple import run_task_agent

async def test():
    user_id = "test_user_123"
    message = "hi"
    print(f"Testing agent with message: {message}")
    try:
        response = await run_task_agent(user_id, message)
        print(f"Agent Response: {response}")
    except Exception as e:
        print(f"Caught top-level exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
