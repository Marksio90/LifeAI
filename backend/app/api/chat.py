from fastapi import APIRouter
from app.services.conversation import ConversationService
from pydantic import BaseModel

router = APIRouter()

class MessageIn(BaseModel):
    session_id: str
    message: str

class SessionIn(BaseModel):
    session_id: str

@router.post("/start")
def start_chat():
    return ConversationService.start_session()

@router.post("/message")
def send_message(data: MessageIn):
    return ConversationService.handle_message(
        session_id=data.session_id,
        user_message=data.message
    )

@router.post("/end")
def end_chat(data: SessionIn):
    return ConversationService.end_session(data.session_id)
