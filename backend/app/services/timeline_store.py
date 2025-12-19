import uuid
import json
from datetime import datetime
from sqlalchemy import text
from app.db import SessionLocal

def save_snapshot(snapshot: dict):
    print("SAVING SNAPSHOT:", snapshot)

    db = SessionLocal()
    try:
        db.execute(
            text("""
                INSERT INTO timeline (
                    id, created_at, summary, themes,
                    core_question, emotional_tone, confidence
                )
                VALUES (
                    :id, :created_at, :summary, :themes,
                    :core_question, :emotional_tone, :confidence
                )
            """),
            {
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow(),
                "summary": snapshot.get("summary"),
                "themes": json.dumps(snapshot.get("themes", [])),
                "core_question": snapshot.get("core_question"),
                "emotional_tone": snapshot.get("emotional_tone"),
                "confidence": snapshot.get("confidence"),
            }
        )
        db.commit()
    finally:
        db.close()
