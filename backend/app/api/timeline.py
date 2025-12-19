from fastapi import APIRouter
from app.services.timeline_store import get_timeline

router = APIRouter(prefix="/timeline", tags=["timeline"])

@router.get("/")
def read_timeline(limit: int = 50):
    """
    Zwraca listę zapisanych snapshotów (timeline).
    """
    items = get_timeline(limit=limit)

    return [
        {
            "id": item.id,
            "created_at": item.created_at,
            "summary": item.summary,
            "themes": item.themes,
            "core_question": item.core_question,
            "emotional_tone": item.emotional_tone,
            "confidence": item.confidence,
        }
        for item in items
    ]
