import uuid
from app.agents.chaos_agent import run_chaos_agent
from app.memory.summarizer import generate_snapshot

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
        snapshot = generate_snapshot(history)
        return {"memory_snapshot": snapshot}
