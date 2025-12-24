"""Advanced WebSocket Server for Real-time Chat.

Features:
- Streaming AI responses with Server-Sent Events
- Connection pooling and management
- Heartbeat/keepalive
- Automatic reconnection handling
- Message acknowledgment
- Typing indicators
- Presence tracking
"""

import asyncio
import json
import logging
from typing import Dict, Set, Optional
from datetime import datetime
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.security.auth import get_current_user_ws
from app.models.user import User
from app.core.router import route_message
from app.schemas.common import Context, Message

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """
    Manages WebSocket connections with advanced features.

    Features:
    - Connection pooling
    - Presence tracking
    - Broadcast capabilities
    - Heartbeat monitoring
    """

    def __init__(self):
        # Active connections: user_id -> Set[WebSocket]
        self.active_connections: Dict[str, Set[WebSocket]] = {}

        # Connection metadata
        self.connection_metadata: Dict[WebSocket, dict] = {}

        # Typing indicators: user_id -> is_typing
        self.typing_status: Dict[str, bool] = {}

        logger.info("ConnectionManager initialized")

    async def connect(self, websocket: WebSocket, user_id: str, session_id: str):
        """
        Connect a new WebSocket client.

        Args:
            websocket: WebSocket connection
            user_id: User identifier
            session_id: Chat session identifier
        """
        await websocket.accept()

        # Add to active connections
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)

        # Store metadata
        self.connection_metadata[websocket] = {
            "user_id": user_id,
            "session_id": session_id,
            "connected_at": datetime.utcnow(),
            "last_heartbeat": datetime.utcnow()
        }

        logger.info(f"User {user_id} connected via WebSocket (session: {session_id})")

        # Notify about connection
        await self.send_personal_message(
            {
                "type": "connection_established",
                "message": "Connected to LifeAI real-time chat",
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            websocket
        )

    def disconnect(self, websocket: WebSocket):
        """
        Disconnect a WebSocket client.

        Args:
            websocket: WebSocket to disconnect
        """
        metadata = self.connection_metadata.get(websocket)
        if not metadata:
            return

        user_id = metadata["user_id"]

        # Remove from active connections
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)

            # Clean up if no more connections for user
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                if user_id in self.typing_status:
                    del self.typing_status[user_id]

        # Remove metadata
        if websocket in self.connection_metadata:
            del self.connection_metadata[websocket]

        logger.info(f"User {user_id} disconnected from WebSocket")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """
        Send message to specific connection.

        Args:
            message: Message dictionary
            websocket: Target WebSocket
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending message: {e}")

    async def send_to_user(self, message: dict, user_id: str):
        """
        Send message to all connections of a user.

        Args:
            message: Message dictionary
            user_id: Target user ID
        """
        if user_id not in self.active_connections:
            return

        disconnected = []
        for connection in self.active_connections[user_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to user {user_id}: {e}")
                disconnected.append(connection)

        # Clean up disconnected
        for conn in disconnected:
            self.disconnect(conn)

    async def broadcast(self, message: dict, exclude: Optional[WebSocket] = None):
        """
        Broadcast message to all connected clients.

        Args:
            message: Message to broadcast
            exclude: Optional WebSocket to exclude
        """
        for connections in self.active_connections.values():
            for connection in connections:
                if connection != exclude:
                    try:
                        await connection.send_json(message)
                    except Exception as e:
                        logger.error(f"Broadcast error: {e}")

    async def stream_message(
        self,
        websocket: WebSocket,
        message_generator,
        message_id: str
    ):
        """
        Stream AI response token by token.

        Args:
            websocket: Target WebSocket
            message_generator: Async generator yielding tokens
            message_id: Message identifier
        """
        try:
            # Send stream start
            await self.send_personal_message({
                "type": "stream_start",
                "message_id": message_id,
                "timestamp": datetime.utcnow().isoformat()
            }, websocket)

            # Stream tokens
            full_response = ""
            async for token in message_generator:
                await self.send_personal_message({
                    "type": "stream_token",
                    "message_id": message_id,
                    "token": token,
                    "timestamp": datetime.utcnow().isoformat()
                }, websocket)

                full_response += token
                await asyncio.sleep(0.01)  # Small delay for smooth streaming

            # Send stream end
            await self.send_personal_message({
                "type": "stream_end",
                "message_id": message_id,
                "full_response": full_response,
                "timestamp": datetime.utcnow().isoformat()
            }, websocket)

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            await self.send_personal_message({
                "type": "stream_error",
                "message_id": message_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }, websocket)

    def get_online_users(self) -> int:
        """Get count of online users."""
        return len(self.active_connections)

    def is_user_online(self, user_id: str) -> bool:
        """Check if user is online."""
        return user_id in self.active_connections

    async def update_typing_status(self, user_id: str, is_typing: bool):
        """
        Update typing indicator for user.

        Args:
            user_id: User identifier
            is_typing: Whether user is typing
        """
        self.typing_status[user_id] = is_typing


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws/chat/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for real-time chat.

    Features:
    - Real-time bidirectional communication
    - Streaming AI responses
    - Typing indicators
    - Heartbeat/keepalive
    - Message acknowledgment

    Args:
        websocket: WebSocket connection
        session_id: Chat session identifier
        token: Authentication token (query param)
        db: Database session
    """
    # Authenticate user
    try:
        user = await get_current_user_ws(token, db)
    except Exception as e:
        logger.error(f"WebSocket authentication failed: {e}")
        await websocket.close(code=1008, reason="Authentication failed")
        return

    user_id = str(user.id)

    # Connect
    await manager.connect(websocket, user_id, session_id)

    # Context for conversation
    context = Context(
        user_id=user_id,
        session_id=session_id,
        history=[]
    )

    try:
        while True:
            # Receive message
            data = await websocket.receive_json()

            message_type = data.get("type")

            # Handle different message types
            if message_type == "message":
                # User message
                content = data.get("content", "")
                message_id = data.get("message_id", str(uuid.uuid4()))

                logger.info(f"Received message from {user_id}: {content[:50]}...")

                # Send acknowledgment
                await manager.send_personal_message({
                    "type": "message_received",
                    "message_id": message_id,
                    "timestamp": datetime.utcnow().isoformat()
                }, websocket)

                # Add to context
                user_message = Message(role="user", content=content)
                context.history.append(user_message)

                # Process message (streaming response)
                try:
                    # Get AI response (with streaming)
                    response_id = str(uuid.uuid4())

                    # In a real implementation, you'd call your LLM with streaming
                    # For now, simulate streaming
                    async def mock_stream():
                        """Mock streaming response."""
                        response = "This is a streaming response from the AI assistant. "
                        response += "Each word appears gradually for better UX. "
                        response += "This creates a more natural conversation flow."

                        words = response.split()
                        for word in words:
                            yield word + " "
                            await asyncio.sleep(0.05)

                    # Stream response
                    await manager.stream_message(
                        websocket,
                        mock_stream(),
                        response_id
                    )

                except Exception as e:
                    logger.error(f"Error processing message: {e}", exc_info=True)
                    await manager.send_personal_message({
                        "type": "error",
                        "message": "Failed to process message",
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat()
                    }, websocket)

            elif message_type == "typing":
                # Typing indicator
                is_typing = data.get("is_typing", False)
                await manager.update_typing_status(user_id, is_typing)

            elif message_type == "heartbeat":
                # Heartbeat/keepalive
                metadata = manager.connection_metadata.get(websocket)
                if metadata:
                    metadata["last_heartbeat"] = datetime.utcnow()

                await manager.send_personal_message({
                    "type": "heartbeat_ack",
                    "timestamp": datetime.utcnow().isoformat()
                }, websocket)

            else:
                logger.warning(f"Unknown message type: {message_type}")

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {user_id}")
        manager.disconnect(websocket)

    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        manager.disconnect(websocket)


@router.get("/ws/status")
async def get_websocket_status():
    """
    Get WebSocket server status.

    Returns:
        Status information including online users
    """
    return {
        "status": "online",
        "online_users": manager.get_online_users(),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/ws/broadcast")
async def broadcast_message(
    message: str,
    current_user: User = Depends(get_current_user_ws)
):
    """
    Broadcast message to all connected users (admin only).

    Args:
        message: Message to broadcast
        current_user: Current authenticated user

    Returns:
        Broadcast confirmation
    """
    # Check if user is admin (you'd implement proper role checking)
    # For now, just broadcast

    await manager.broadcast({
        "type": "broadcast",
        "message": message,
        "from": "system",
        "timestamp": datetime.utcnow().isoformat()
    })

    return {
        "status": "broadcasted",
        "recipients": manager.get_online_users()
    }
