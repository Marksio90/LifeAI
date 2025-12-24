"""Database session management and configuration"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

logger = logging.getLogger(__name__)

# Get database URL from environment (required)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Optimized connection pool configuration
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "20"))  # Base pool size (increased from 5)
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "40"))  # Max overflow connections (increased from 10)
POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))  # Connection timeout in seconds
POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))  # Recycle connections after 1 hour
POOL_PRE_PING = os.getenv("DB_POOL_PRE_PING", "true").lower() == "true"

# Create SQLAlchemy engine with optimized pooling
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=POOL_PRE_PING,  # Verify connections before using (prevents stale connections)
    pool_size=POOL_SIZE,  # Number of connections to maintain in pool
    max_overflow=MAX_OVERFLOW,  # Additional connections beyond pool_size
    pool_timeout=POOL_TIMEOUT,  # Seconds to wait before giving up on getting connection
    pool_recycle=POOL_RECYCLE,  # Recycle connections older than this (prevents stale MySQL connections)
    echo=False,  # Set to True for SQL query logging in development
    pool_use_lifo=True,  # Use LIFO (last in first out) for better connection reuse
    echo_pool=False,  # Set to True to debug connection pool
    connect_args={
        "connect_timeout": 10,  # Connection timeout in seconds
    } if "postgresql" in DATABASE_URL.lower() else {}
)

logger.info(
    f"Database connection pool configured: "
    f"pool_size={POOL_SIZE}, max_overflow={MAX_OVERFLOW}, "
    f"timeout={POOL_TIMEOUT}s, recycle={POOL_RECYCLE}s"
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Database dependency for FastAPI endpoints.

    Usage:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            items = db.query(Item).all()
            return items

    Yields:
        SQLAlchemy Session object
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database - create all tables.

    This should be called during application startup.
    In production, use Alembic migrations instead.
    """
    from app.db.base import Base
    from app.models import User, Conversation, Feedback, AgentInteraction

    logger.info("Initializing database...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully")


def check_db_connection() -> bool:
    """
    Check if database connection is working.

    Returns:
        True if connection successful, False otherwise
    """
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
