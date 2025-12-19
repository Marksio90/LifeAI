"""
FastAPI Application - Main Entry Point
Exposes REST API for the LifeAI Platform
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

from loguru import logger

from src.core import (
    CoreOrchestrator, IntentRecognizer, ResponseMerger,
    UserInput, OrchestratorResponse
)
from src.core.identity_engine import IdentityEngine
from src.memory.memory_system import MemorySystem
from src.agents.health.health_agent import HealthAgent
from src.agents.finance.finance_agent import FinanceAgent
from src.agents.psychology.psychology_agent import PsychologyAgent
from config import settings


# Initialize FastAPI app
app = FastAPI(
    title="LifeAI Platform",
    description="Advanced AI-powered Life Guidance System",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class ChatRequest(BaseModel):
    user_id: str
    session_id: Optional[str] = None
    message: str
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    session_id: str
    response: str
    confidence: float
    intent: str
    agents_used: list
    timestamp: str


class SessionRequest(BaseModel):
    user_id: str


class SessionResponse(BaseModel):
    session_id: str
    user_id: str
    created_at: str


class FeedbackRequest(BaseModel):
    session_id: str
    message_index: int
    helpful: bool
    rating: Optional[int] = None
    comment: Optional[str] = None


# Global instances (in production, use dependency injection)
orchestrator: Optional[CoreOrchestrator] = None
identity_engine: Optional[IdentityEngine] = None
memory_system: Optional[MemorySystem] = None


@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    global orchestrator, identity_engine, memory_system

    logger.info("Starting LifeAI Platform...")

    # Initialize components
    intent_recognizer = IntentRecognizer()
    response_merger = ResponseMerger()
    identity_engine = IdentityEngine()
    memory_system = MemorySystem()

    # Initialize orchestrator
    orchestrator = CoreOrchestrator(
        intent_recognizer=intent_recognizer,
        response_merger=response_merger,
        max_agents=5,
        confidence_threshold=0.6
    )

    # Register agents
    health_agent = HealthAgent()
    finance_agent = FinanceAgent()
    psychology_agent = PsychologyAgent()

    orchestrator.register_agent("health", health_agent)
    orchestrator.register_agent("finance", finance_agent)
    orchestrator.register_agent("psychology", psychology_agent)

    logger.info("LifeAI Platform started successfully!")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "LifeAI Platform",
        "version": "0.1.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "components": {
            "orchestrator": orchestrator is not None,
            "identity_engine": identity_engine is not None,
            "memory_system": memory_system is not None
        },
        "statistics": {
            "orchestrator": orchestrator.get_statistics() if orchestrator else {},
            "memory": memory_system.get_statistics() if memory_system else {}
        }
    }


@app.post("/session/create", response_model=SessionResponse)
async def create_session(request: SessionRequest):
    """Create new conversation session"""
    try:
        session_id = str(uuid.uuid4())

        # Get user context
        user_context = await identity_engine.get_context(request.user_id)

        # Create session in memory system
        await memory_system.create_session(
            session_id=session_id,
            user_id=request.user_id,
            initial_context=user_context
        )

        return SessionResponse(
            session_id=session_id,
            user_id=request.user_id,
            created_at=datetime.utcnow().isoformat()
        )

    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint
    Processes user message and returns AI response
    """
    try:
        # Create or get session
        session_id = request.session_id or str(uuid.uuid4())

        # Get user context
        user_context = await identity_engine.get_context(
            request.user_id,
            include_history=True
        )

        # Merge with provided context
        if request.context:
            user_context.update(request.context)

        # Get conversation history
        conversation_history = await memory_system.get_context(
            session_id,
            max_messages=10
        )

        # Add conversation history to context
        if conversation_history:
            user_context["conversation_history"] = conversation_history

        # Create user input
        user_input = UserInput(
            user_id=request.user_id,
            session_id=session_id,
            content=request.message,
            input_type="text"
        )

        # Add user message to memory
        await memory_system.add_message(
            session_id=session_id,
            role="user",
            content=request.message
        )

        # Process through orchestrator
        result: OrchestratorResponse = await orchestrator.process_input(
            user_input,
            user_context
        )

        # Add assistant response to memory
        await memory_system.add_message(
            session_id=session_id,
            role="assistant",
            content=result.content,
            metadata={
                "confidence": result.total_confidence,
                "intent": result.intent.intent_type.value,
                "agents": [r.agent_id for r in result.agent_responses]
            }
        )

        # Return response
        return ChatResponse(
            session_id=session_id,
            response=result.content,
            confidence=result.total_confidence,
            intent=result.intent.intent_type.value,
            agents_used=[r.agent_id for r in result.agent_responses],
            timestamp=result.timestamp.isoformat()
        )

    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Submit feedback on a response"""
    try:
        feedback = {
            "helpful": request.helpful,
            "rating": request.rating,
            "comment": request.comment
        }

        await memory_system.store_feedback(
            session_id=request.session_id,
            message_index=request.message_index,
            feedback=feedback
        )

        return {"status": "success", "message": "Feedback recorded"}

    except Exception as e:
        logger.error(f"Error storing feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/profile/{user_id}")
async def get_profile(user_id: str):
    """Get user profile"""
    try:
        profile = await identity_engine.get_or_create_profile(user_id)
        return profile.dict()

    except Exception as e:
        logger.error(f"Error getting profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/profile/{user_id}/update")
async def update_profile(user_id: str, updates: Dict[str, Any]):
    """Update user profile"""
    try:
        profile = await identity_engine.update_profile(user_id, updates)
        return {"status": "success", "profile": profile.dict()}

    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/statistics")
async def get_statistics():
    """Get system statistics"""
    return {
        "orchestrator": orchestrator.get_statistics() if orchestrator else {},
        "memory": memory_system.get_statistics() if memory_system else {}
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
