from fastapi import APIRouter, HTTPException
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
async def chat_simple(request: ChatRequest):
    """
    Chat endpoint that uses the MCP-enabled TaskAssistant.
    The agent connects to the TaskManager MCP server for task management.
    """
    try:
        logger.info(f"Received chat request: {request.message} (Session: {request.session_id}, User: {request.user_id})")
        
        # Run the MCP-enabled agent
        response = await run_task_agent(request.user_id, request.message)
        
        return ChatResponse(response=response)
    except Exception as e:
        logger.error(f"Error in chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
