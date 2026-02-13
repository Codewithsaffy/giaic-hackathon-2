from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import logging

# Import the MCP-enabled agent runner
from agent_simple import run_task_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    session_id: str
    user_id: str

class ChatResponse(BaseModel):
    response: str

@router.post("/simple", response_model=ChatResponse)
async def chat_simple(request_data: ChatRequest, request: Request):
    """
    Chat endpoint that uses the MCP-enabled TaskAssistant.
    Reuses the persistent MCP server from the application state.
    """
    try:
        logger.info(f"Received chat request: {request_data.message} (Session: {request_data.session_id}, User: {request_data.user_id})")
        
        # Pull persistent MCP from app state (initialized in main.py)
        mcp_server = getattr(request.app.state, "mcp_server", None)
        if mcp_server:
            logger.info("Reusing persistent TaskManager MCP server.")
        else:
            logger.warning("Persistent MCP server not found in app state, falling back to one-off.")

        # Run the agent with the persistent server
        response = await run_task_agent(request_data.user_id, request_data.message, mcp_server=mcp_server)
        
        return ChatResponse(response=response)
    except Exception as e:
        logger.error(f"Error in chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
