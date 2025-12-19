import json
from typing import List, Dict
from app.services.llm_client import call_llm

def generate_snapshot(history: list[dict]) -> str:
    if not history:
        return json.dumps(DEFAULT_SNAPSHOT)

    prompt = f"""
You are an analytical assistant.

Summarize the following conversation as a structured JSON.
You MUST return valid JSON only. No commentary.

Required JSON schema:
{{
  "summary": string or null,
  "themes": array of short strings,
  "core_question": string or null,
  "emotional_tone": one of ["sad", "neutral", "anxious", "hopeful", "angry"] or null,
  "confidence": float between 0 and 1
}}

Conversation:
{json.dumps(history, ensure_ascii=False)}
"""

    try:
        messages = [{"role": "system", "content": prompt}]
        raw = call_llm(messages)

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
