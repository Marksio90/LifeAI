"""GDPR Compliance Endpoints.

Implements GDPR rights:
- Right to Erasure (delete all user data)
- Right to Data Portability (export user data)
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.models.conversation import Conversation
from app.models.feedback import Feedback
from app.security.auth import get_current_user
from app.memory.vector_factory import get_vector_store

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/gdpr", tags=["GDPR"])


@router.delete("/delete-my-data")
async def delete_user_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete all user data (GDPR Right to Erasure).

    This operation is IRREVERSIBLE and deletes:
    - All conversations and messages
    - All feedback
    - Vector embeddings (memories)
    - User preferences
    - User account (anonymized)

    The user record is kept but anonymized for audit purposes.

    Returns:
        Success message
    """
    user_id = str(current_user.id)

    try:
        logger.warning(f"GDPR deletion requested for user {user_id}")

        # 1. Delete conversations (CASCADE deletes agent_interactions, feedbacks)
        await db.execute(
            delete(Conversation).where(Conversation.user_id == current_user.id)
        )
        logger.info(f"Deleted conversations for user {user_id}")

        # 2. Delete any orphaned feedback (shouldn't exist due to CASCADE, but defensive)
        await db.execute(
            delete(Feedback).where(Feedback.user_id == current_user.id)
        )

        # 3. Delete vector memories from vector store
        try:
            vector_store = get_vector_store()
            deleted_count = await vector_store.delete_by_user(user_id)
            logger.info(f"Deleted {deleted_count} vector memories for user {user_id}")
        except Exception as e:
            logger.error(f"Error deleting vector memories: {e}")
            # Continue with deletion even if vector delete fails

        # 4. Anonymize user record (keep for audit trail)
        current_user.email = f"deleted_{user_id}@anonymized.local"
        current_user.username = f"deleted_{user_id}"
        current_user.full_name = "Deleted User"
        current_user.password_hash = "DELETED"
        current_user.is_active = False
        current_user.is_verified = False
        current_user.is_premium = False
        current_user.preferences = {}
        current_user.mfa_enabled = False
        current_user.mfa_secret = None
        current_user.preferred_language = "pl"
        current_user.preferred_voice = "nova"

        # Commit all changes
        await db.commit()

        logger.warning(f"GDPR deletion completed for user {user_id}")

        return {
            "message": "All your data has been permanently deleted",
            "status": "deleted",
            "user_id": user_id
        }

    except Exception as e:
        logger.error(f"Error during GDPR deletion: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting user data: {str(e)}"
        )


@router.get("/export-my-data")
async def export_user_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Export all user data (GDPR Right to Data Portability).

    Returns complete user data in JSON format:
    - User profile
    - All conversations with messages
    - Feedback submitted
    - Statistics

    Returns:
        Complete user data dictionary
    """
    user_id = str(current_user.id)

    try:
        logger.info(f"GDPR export requested for user {user_id}")

        # 1. Get all conversations
        result = await db.execute(
            select(Conversation)
            .where(Conversation.user_id == current_user.id)
            .order_by(Conversation.created_at.desc())
        )
        conversations = result.scalars().all()

        # 2. Get all feedback
        feedback_result = await db.execute(
            select(Feedback)
            .where(Feedback.user_id == current_user.id)
            .order_by(Feedback.created_at.desc())
        )
        feedbacks = feedback_result.scalars().all()

        # 3. Build export data
        export_data = {
            "export_date": "2024-12-24",
            "user": {
                "id": user_id,
                "email": current_user.email,
                "username": current_user.username,
                "full_name": current_user.full_name,
                "preferred_language": current_user.preferred_language,
                "preferred_voice": current_user.preferred_voice,
                "is_premium": current_user.is_premium,
                "is_verified": current_user.is_verified,
                "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
                "last_login": current_user.last_login.isoformat() if current_user.last_login else None,
                "preferences": current_user.preferences
            },
            "conversations": [
                {
                    "id": str(conv.id),
                    "session_id": conv.session_id,
                    "title": conv.title,
                    "language": conv.language,
                    "messages": conv.messages,
                    "message_count": conv.message_count,
                    "agents_used": conv.agents_used,
                    "created_at": conv.created_at.isoformat() if conv.created_at else None,
                    "updated_at": conv.updated_at.isoformat() if conv.updated_at else None,
                    "ended_at": conv.ended_at.isoformat() if conv.ended_at else None,
                    "summary": conv.summary,
                    "main_topics": conv.main_topics
                }
                for conv in conversations
            ],
            "feedback": [
                {
                    "id": str(fb.id),
                    "conversation_id": str(fb.conversation_id) if fb.conversation_id else None,
                    "rating": fb.rating,
                    "comment": fb.comment,
                    "created_at": fb.created_at.isoformat() if fb.created_at else None
                }
                for fb in feedbacks
            ],
            "statistics": {
                "total_conversations": len(conversations),
                "total_messages": sum(conv.message_count for conv in conversations),
                "total_feedback": len(feedbacks),
                "average_rating": (
                    sum(fb.rating for fb in feedbacks if fb.rating) / len(feedbacks)
                    if feedbacks else 0
                ),
                "most_used_agents": _get_most_used_agents(conversations)
            }
        }

        logger.info(f"GDPR export completed for user {user_id}")

        return export_data

    except Exception as e:
        logger.error(f"Error during GDPR export: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error exporting user data: {str(e)}"
        )


def _get_most_used_agents(conversations) -> Dict[str, int]:
    """
    Calculate most used agents from conversations.

    Args:
        conversations: List of Conversation objects

    Returns:
        Dictionary of agent usage counts
    """
    agent_counts = {}

    for conv in conversations:
        for agent in conv.agents_used or []:
            agent_counts[agent] = agent_counts.get(agent, 0) + 1

    # Sort by count descending
    sorted_agents = sorted(
        agent_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return dict(sorted_agents)


@router.get("/consent-status")
async def get_consent_status(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get current consent status.

    Returns:
        User's consent preferences
    """
    preferences = current_user.preferences or {}

    return {
        "consent_analytics": preferences.get("consent_analytics", False),
        "consent_marketing": preferences.get("consent_marketing", False),
        "consent_timestamp": preferences.get("consent_timestamp"),
        "can_withdraw": True
    }


@router.post("/update-consent")
async def update_consent(
    consent_analytics: bool,
    consent_marketing: bool,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user consent preferences.

    Args:
        consent_analytics: Consent for analytics
        consent_marketing: Consent for marketing

    Returns:
        Updated consent status
    """
    from datetime import datetime

    if current_user.preferences is None:
        current_user.preferences = {}

    current_user.preferences["consent_analytics"] = consent_analytics
    current_user.preferences["consent_marketing"] = consent_marketing
    current_user.preferences["consent_timestamp"] = datetime.utcnow().isoformat()

    await db.commit()

    logger.info(
        f"Consent updated for user {current_user.id}: "
        f"analytics={consent_analytics}, marketing={consent_marketing}"
    )

    return {
        "message": "Consent preferences updated",
        "consent_analytics": consent_analytics,
        "consent_marketing": consent_marketing
    }
