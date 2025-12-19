import json
from datetime import datetime
import uuid

def generate_snapshot(history: list[dict]) -> str:
    if not history:
        return ""

    user_messages = [m["content"] for m in history if m["role"] == "user"]

    summary = user_messages[-1] if user_messages else None

    snapshot = {
        "id": str(uuid.uuid4()),
        "created_at": datetime.utcnow().isoformat(),
        "summary": summary,
        "themes": None,
        "core_question": None,
        "emotional_tone": None,
        "confidence": None,
    }

    return json.dumps(snapshot)
