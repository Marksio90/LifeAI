from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.api.chat import router as chat_router
from app.api.timeline import router as timeline_router
from app.api.multimodal import router as multimodal_router
from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.api.metrics import router as metrics_router
from app.middleware.prometheus_middleware import PrometheusMiddleware
from app.core import initialize_agents
from app.core.config import get_settings

# Load settings
settings = get_settings()

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
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Prometheus middleware (collect HTTP metrics)
app.add_middleware(PrometheusMiddleware)

# ROUTERS
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(timeline_router)
app.include_router(multimodal_router)
app.include_router(metrics_router)


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
