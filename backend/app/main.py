from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.api.chat import router as chat_router
from app.api.timeline import router as timeline_router
from app.api.multimodal import router as multimodal_router
from app.core import initialize_agents

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for application startup and shutdown.
    """
    # Startup
    logger.info("Starting LifeAI application...")
    initialize_agents()
    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down LifeAI application...")


app = FastAPI(
    title="LifeAI - Multi-Agent AI Platform",
    description="Wieloagentowa platforma AI wspierająca użytkowników w życiu codziennym",
    version="2.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROUTERS
app.include_router(chat_router)
app.include_router(timeline_router)
app.include_router(multimodal_router)


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok", "version": "2.1.0"}


@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "name": "LifeAI API",
        "version": "2.1.0",
        "description": "Multi-agent AI platform",
        "endpoints": {
            "health": "/health",
            "chat": "/chat",
            "timeline": "/timeline",
            "docs": "/docs"
        }
    }
