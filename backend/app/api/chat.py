from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from typing import Optional, List
from sqlalchemy.orm import Session
from app.core.orchestrator import get_orchestrator
from app.schemas.common import Language
from app.models.user import User
from app.models.conversation import Conversation
from app.security.auth import get_current_user
from app.db.session import get_db
from app.middleware.rate_limit import chat_limiter
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
    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="User message (max 4000 characters to prevent DoS)"
    )
    metadata: Optional[dict] = Field(
        default=None,
        description="Optional metadata (e.g., modality: text/voice/image)"
    )


class SessionEndRequest(BaseModel):
    """Request to end a session"""
    session_id: str


@router.post("/start")
async def start_chat(
    request: SessionCreateRequest = SessionCreateRequest(),
    current_user: User = Depends(get_current_user)
):
    """
    Start a new chat session.

    Returns:
        session_id and initial information
    """
    try:
        orchestrator = get_orchestrator()
        session_id = orchestrator.create_session(
            user_id=str(current_user.id),
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
async def send_message(
    data: MessageRequest,
    _: None = Depends(chat_limiter)
):
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
            user_message=data.message,
            message_metadata=data.metadata
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


@router.get("/conversation/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get full conversation history by ID.

    Returns:
        Full conversation with all messages
    """
    try:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == str(current_user.id)
        ).first()

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        logger.info(f"Retrieved conversation {conversation_id} for user {current_user.id}")

        return {
            "id": str(conversation.id),
            "session_id": conversation.session_id,
            "title": conversation.title,
            "language": conversation.language,
            "messages": conversation.messages or [],
            "message_count": conversation.message_count,
            "agents_used": conversation.agents_used or [],
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat() if conversation.updated_at else None,
            "ended_at": conversation.ended_at.isoformat() if conversation.ended_at else None,
            "summary": conversation.summary,
            "main_topics": conversation.main_topics or []
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve conversation")


@router.post("/resume/{conversation_id}")
async def resume_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Resume a previous conversation by creating a new session with conversation history.

    Returns:
        New session_id with loaded conversation history
    """
    try:
        # Get conversation from database
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == str(current_user.id)
        ).first()

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        orchestrator = get_orchestrator()

        # Create new session with user ID and language
        language = Language(conversation.language) if conversation.language else Language.POLISH
        session_id = orchestrator.create_session(
            user_id=str(current_user.id),
            language=language
        )

        # Load previous messages into the new session context
        context = orchestrator.get_session(session_id)
        if context and conversation.messages:
            from app.schemas.common import Message
            from datetime import datetime

            # Reconstruct message history
            for msg in conversation.messages:
                context.history.append(Message(
                    role=msg.get("role", "user"),
                    content=msg.get("content", ""),
                    timestamp=datetime.fromisoformat(msg.get("timestamp")) if msg.get("timestamp") else datetime.utcnow(),
                    metadata=msg.get("metadata", {})
                ))

        logger.info(f"Resumed conversation {conversation_id} as new session {session_id} for user {current_user.id}")

        return {
            "session_id": session_id,
            "conversation_id": conversation_id,
            "language": language.value,
            "message_count": len(conversation.messages) if conversation.messages else 0,
            "message": f"Resumed conversation: {conversation.title or 'Untitled'}"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resuming conversation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to resume conversation")
