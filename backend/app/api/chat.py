from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from app.core.orchestrator import get_orchestrator
from app.schemas.common import Language
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


class SessionCreateRequest(BaseModel):
    """Request to create a new chat session"""
    user_id: Optional[str] = None
    language: Language = Language.POLISH


class MessageRequest(BaseModel):
    """Request to send a message"""
    session_id: str
    message: str = Field(..., min_length=1)


class SessionEndRequest(BaseModel):
    """Request to end a session"""
    session_id: str


@router.post("/start")
async def start_chat(request: SessionCreateRequest = SessionCreateRequest()):
    """
    Start a new chat session.

    Returns:
        session_id and initial information
    """
    try:
        orchestrator = get_orchestrator()
        session_id = orchestrator.create_session(
            user_id=request.user_id,
            language=request.language
        )

        logger.info(f"Created new chat session: {session_id}")

        return {
            "session_id": session_id,
            "language": request.language.value,
            "message": "Session created successfully. How can I help you today?"
        }

    except Exception as e:
        logger.error(f"Error creating session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create session")


@router.post("/message")
async def send_message(data: MessageRequest):
    """
    Send a message to the AI assistant.

    The message will be routed to the appropriate agent(s) based on intent.

    Returns:
        AI response with metadata about which agent(s) handled the request
    """
    try:
        orchestrator = get_orchestrator()

        # Process message through multi-agent system
        response = await orchestrator.process_message(
            session_id=data.session_id,
            user_message=data.message
        )

        return {
            "reply": response.content,
            "metadata": {
                "agents_used": [ar.agent_id for ar in response.agent_responses],
                "routing_type": response.metadata.get("routing_type"),
                "confidence": response.metadata.get("confidence")
            }
        }

    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process message")


@router.post("/end")
async def end_chat(data: SessionEndRequest):
    """
    End a chat session.

    This will generate a summary and clean up the session.

    Returns:
        Success status and optional session summary
    """
    try:
        orchestrator = get_orchestrator()
        success = orchestrator.end_session(data.session_id)

        if not success:
            raise HTTPException(status_code=404, detail="Session not found")

        logger.info(f"Ended chat session: {data.session_id}")

        return {
            "success": True,
            "message": "Session ended successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to end session")


@router.get("/session/{session_id}")
async def get_session_info(session_id: str):
    """
    Get information about a session.

    Returns:
        Session context and history
    """
    try:
        orchestrator = get_orchestrator()
        context = orchestrator.get_session(session_id)

        if not context:
            raise HTTPException(status_code=404, detail="Session not found")

        return {
            "session_id": context.session_id,
            "language": context.language.value,
            "message_count": len(context.history),
            "created_at": context.metadata.get("created_at")
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session info: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get session info")


@router.get("/stats")
async def get_stats():
    """
    Get orchestrator statistics.

    Returns:
        Statistics about active sessions and agents
    """
    try:
        orchestrator = get_orchestrator()
        stats = orchestrator.get_stats()

        return stats

    except Exception as e:
        logger.error(f"Error getting stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get stats")
