"""Timeline API - User conversation history endpoints"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, cast, String
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.db.session import get_db
from app.models.conversation import Conversation
from app.models.user import User
from app.security.auth import get_current_user
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/timeline", tags=["timeline"])


class ConversationSummary(BaseModel):
    """Summary of a conversation for timeline view"""
    id: str
    session_id: str
    title: Optional[str]
    message_count: int
    agents_used: List[str]
    created_at: str
    updated_at: Optional[str]
    summary: Optional[str]
    main_topics: List[str]


class ConversationDetail(BaseModel):
    """Detailed conversation with messages"""
    id: str
    session_id: str
    title: Optional[str]
    language: str
    messages: List[dict]
    message_count: int
    agents_used: List[str]
    created_at: str
    updated_at: Optional[str]
    ended_at: Optional[str]
    summary: Optional[str]
    main_topics: List[str]


@router.get("/", response_model=List[ConversationSummary])
async def get_current_user_timeline(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    days: Optional[int] = Query(None, ge=1, le=365),
    search: Optional[str] = Query(None, description="Search in title and messages"),
    sort_by: str = Query("created_at", description="Sort field: created_at, message_count, title"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get timeline for currently authenticated user with search and filtering.

    Returns conversations sorted by most recent first by default.

    Query Parameters:
    - search: Search in conversation title and message content
    - days: Filter conversations from last N days
    - sort_by: Field to sort by (created_at, message_count, title)
    - sort_order: Sort order (asc or desc)
    - limit: Max results (1-100)
    - offset: Pagination offset
    """
    try:
        query = db.query(Conversation).filter(Conversation.user_id == str(current_user.id))

        # Search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Conversation.title.ilike(search_term),
                    Conversation.summary.ilike(search_term),
                    cast(Conversation.messages, String).ilike(search_term)
                )
            )

        # Filter by date range if specified
        if days:
            since = datetime.utcnow() - timedelta(days=days)
            query = query.filter(Conversation.created_at >= since)

        # Sorting
        sort_column = Conversation.created_at  # default
        if sort_by == "message_count":
            sort_column = Conversation.message_count
        elif sort_by == "title":
            sort_column = Conversation.title

        if sort_order.lower() == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        # Apply pagination
        conversations = query.offset(offset).limit(limit).all()

        logger.info(f"Retrieved {len(conversations)} conversations for user {current_user.id}")

        result = [
            ConversationSummary(
                id=str(conv.id),
                session_id=conv.session_id,
                title=conv.title or f"Conversation from {conv.created_at.strftime('%Y-%m-%d %H:%M')}",
                message_count=conv.message_count,
                agents_used=conv.agents_used or [],
                created_at=conv.created_at.isoformat(),
                updated_at=conv.updated_at.isoformat() if conv.updated_at else None,
                summary=conv.summary,
                main_topics=conv.main_topics or []
            )
            for conv in conversations
        ]

        # Debug logging
        logger.info(f"Returning timeline data: {len(result)} items")
        if result:
            logger.info(f"First item: id={result[0].id}, title={result[0].title}, messages={result[0].message_count}")

        return result

    except Exception as e:
        logger.error(f"Error fetching timeline: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch timeline")


@router.get("/conversations", response_model=List[ConversationSummary])
async def get_user_conversations(
    user_id: str = Query(..., description="User ID to fetch conversations for"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of conversations to return"),
    offset: int = Query(0, ge=0, description="Number of conversations to skip"),
    days: Optional[int] = Query(None, ge=1, le=365, description="Filter conversations from last N days"),
    db: Session = Depends(get_db)
):
    """
    Get all conversations for a user (timeline view).

    Returns conversations sorted by most recent first.
    """
    try:
        query = db.query(Conversation).filter(Conversation.user_id == user_id)

        # Filter by date range if specified
        if days:
            since = datetime.utcnow() - timedelta(days=days)
            query = query.filter(Conversation.created_at >= since)

        # Order by most recent first
        query = query.order_by(Conversation.created_at.desc())

        # Apply pagination
        conversations = query.offset(offset).limit(limit).all()

        logger.info(f"Retrieved {len(conversations)} conversations for user {user_id}")

        return [
            ConversationSummary(
                id=str(conv.id),
                session_id=conv.session_id,
                title=conv.title or f"Conversation from {conv.created_at.strftime('%Y-%m-%d %H:%M')}",
                message_count=conv.message_count,
                agents_used=conv.agents_used or [],
                created_at=conv.created_at.isoformat(),
                updated_at=conv.updated_at.isoformat() if conv.updated_at else None,
                summary=conv.summary,
                main_topics=conv.main_topics or []
            )
            for conv in conversations
        ]

    except Exception as e:
        logger.error(f"Error fetching conversations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch conversations")


@router.get("/conversation/{conversation_id}", response_model=ConversationDetail)
async def get_conversation_detail(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific conversation including all messages.
    """
    try:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        logger.info(f"Retrieved conversation {conversation_id}")

        return ConversationDetail(
            id=str(conversation.id),
            session_id=conversation.session_id,
            title=conversation.title or f"Conversation from {conversation.created_at.strftime('%Y-%m-%d %H:%M')}",
            language=conversation.language,
            messages=conversation.messages or [],
            message_count=conversation.message_count,
            agents_used=conversation.agents_used or [],
            created_at=conversation.created_at.isoformat(),
            updated_at=conversation.updated_at.isoformat() if conversation.updated_at else None,
            ended_at=conversation.ended_at.isoformat() if conversation.ended_at else None,
            summary=conversation.summary,
            main_topics=conversation.main_topics or []
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching conversation detail: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch conversation")


@router.delete("/conversation/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a specific conversation.
    """
    try:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        db.delete(conversation)
        db.commit()

        logger.info(f"Deleted conversation {conversation_id}")

        return {
            "success": True,
            "message": "Conversation deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete conversation")


@router.get("/stats/{user_id}")
async def get_user_stats(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get statistics about a user's conversations.

    Returns:
        Total conversations, message count, most used agents, etc.
    """
    try:
        # Get all conversations for user
        conversations = db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).all()

        total_conversations = len(conversations)
        total_messages = sum(conv.message_count for conv in conversations)

        # Count agent usage
        agent_usage = {}
        for conv in conversations:
            for agent in conv.agents_used or []:
                agent_usage[agent] = agent_usage.get(agent, 0) + 1

        # Get recent activity (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_conversations = [
            conv for conv in conversations
            if conv.created_at >= week_ago
        ]

        logger.info(f"Retrieved stats for user {user_id}")

        return {
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "agent_usage": agent_usage,
            "recent_activity": {
                "conversations_last_7_days": len(recent_conversations),
                "messages_last_7_days": sum(conv.message_count for conv in recent_conversations)
            },
            "most_used_agents": sorted(
                agent_usage.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5] if agent_usage else []
        }

    except Exception as e:
        logger.error(f"Error fetching user stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch user stats")
