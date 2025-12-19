import uuid
import json
from app.agents.chaos_agent import run_chaos_agent
from app.memory.summarizer import generate_snapshot
from app.services.timeline_store import save_snapshot

SESSIONS = {}

class ConversationService:

    @staticmethod
    def start_session():
        session_id = str(uuid.uuid4())
        SESSIONS[session_id] = []
        return {"session_id": session_id}

    @staticmethod
    def handle_message(session_id: str, user_message: str):
        history = SESSIONS.get(session_id, [])

        history.append({"role": "user", "content": user_message})
        assistant_reply = run_chaos_agent(history)
        history.append({"role": "assistant", "content": assistant_reply})

        SESSIONS[session_id] = history
        return {"reply": assistant_reply}

    @staticmethod
    def end_session(session_id: str):
        history = SESSIONS.get(session_id, [])

        snapshot_json = generate_snapshot(history)

        try:
            snapshot = json.loads(snapshot_json)
        except json.JSONDecodeError:
            snapshot = None

        if snapshot:
            save_snapshot(snapshot)

        return {"memory_snapshot": snapshot}

