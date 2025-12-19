import json
from typing import List, Dict
from app.llm.client import call_llm  # dostosuj jeśli masz inną nazwę

DEFAULT_SNAPSHOT = {
    "summary": None,
    "themes": [],
    "core_question": None,
    "emotional_tone": None,
    "confidence": 0.0,
}

def generate_snapshot(history: List[Dict]) -> str:
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
        raw = call_llm(prompt)

        data = json.loads(raw)

        # 🔒 WALIDACJA POL
        snapshot = {
            "summary": data.get("summary"),
            "themes": data.get("themes", []),
            "core_question": data.get("core_question"),
            "emotional_tone": data.get("emotional_tone"),
            "confidence": float(data.get("confidence", 0.0)),
        }

        return json.dumps(snapshot)

    except Exception as e:
        print("SNAPSHOT ERROR:", e)
        return json.dumps(DEFAULT_SNAPSHOT)
