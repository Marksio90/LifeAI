import uuid
from datetime import datetime
from sqlalchemy import text
from app.db.session import SessionLocal
from app.models.timeline import Timeline


def save_snapshot(snapshot: dict):
    """
    Zapisuje snapshot rozmowy do tabeli timeline.
    Snapshot powinien być słownikiem z kluczami:
    summary, themes, core_question, emotional_tone, confidence
    """

    print("SAVING SNAPSHOT:", snapshot)

    db = SessionLocal()
    try:
        db.execute(
            text("""
                INSERT INTO timeline (
                    id,
                    created_at,
                    summary,
                    themes,
                    core_question,
                    emotional_tone,
                    confidence
                )
                VALUES (
                    :id,
                    :created_at,
                    :summary,
                    :themes,
                    :core_question,
                    :emotional_tone,
                    :confidence
                )
            """),
            {
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow(),
                "summary": snapshot.get("summary"),
                "themes": snapshot.get("themes"),
                "core_question": snapshot.get("core_question"),
                "emotional_tone": snapshot.get("emotional_tone"),
                "confidence": snapshot.get("confidence"),
            }
        )
        db.commit()
    except Exception as e:
        db.rollback()
        print("ERROR SAVING SNAPSHOT:", e)
        raise
    finally:
        db.close()


def get_timeline(limit: int = 50):
    """
    Zwraca ostatnie wpisy timeline (domyślnie 50),
    posortowane od najnowszych.
    """

    db = SessionLocal()
    try:
        return (
            db.query(Timeline)
            .order_by(Timeline.created_at.desc())
            .limit(limit)
            .all()
        )
    finally:
        db.close()
