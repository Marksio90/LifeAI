"""Server-Sent Events (SSE) streaming for real-time LLM responses."""
import asyncio
import json
import logging
from typing import AsyncGenerator, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.security.auth import get_current_user
from app.models.user import User
from app.core.orchestrator import get_orchestrator
from app.middleware.rate_limit import chat_limiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat-streaming"])


class StreamMessageRequest(BaseModel):
    """Request to stream a message"""
    session_id: str
    message: str = Field(..., min_length=1, max_length=4000)
    metadata: Optional[dict] = None


async def stream_agent_response(
    session_id: str,
    user_message: str,
    user_id: str,
    metadata: Optional[dict] = None
) -> AsyncGenerator[str, None]:
    """
    Stream LLM response tokens as they arrive.

    Yields Server-Sent Events in the format:
    data: {"type": "token", "content": "word"}
    data: {"type": "metadata", "agent_id": "finance", "confidence": 0.95}
    data: {"type": "done"}

    Args:
        session_id: Chat session ID
        user_message: User's message
        user_id: User ID for authentication
        metadata: Optional message metadata

    Yields:
        SSE formatted strings
    """
    try:
        # Import here to avoid circular dependency
        from app.services.llm_client import aclient
        from app.core.router import route_message

        # Get orchestrator and session
        orchestrator = get_orchestrator()
        context = orchestrator.get_session(session_id)

        if not context:
            yield f"data: {json.dumps({'type': 'error', 'message': 'Session not found'})}\n\n"
            return

        # Verify session ownership
        if context.user_id != user_id:
            yield f"data: {json.dumps({'type': 'error', 'message': 'Unauthorized'})}\n\n"
            return

        # Route message to get agent info (but don't execute yet)
        routing_decision = await route_message(user_message, context)

        # Send metadata about which agent will handle this
        yield f"data: {json.dumps({
            'type': 'metadata',
            'agents': [r.agent_id for r in routing_decision.agent_responses],
            'routing_type': routing_decision.metadata.get('routing_type'),
            'confidence': routing_decision.metadata.get('confidence')
        })}\n\n"

        # Build messages for LLM
        from app.schemas.common import Message
        from datetime import datetime, timezone

        # Add user message to history
        user_msg = Message(
            role="user",
            content=user_message,
            timestamp=datetime.now(timezone.utc),
            metadata=metadata or {}
        )
        context.history.append(user_msg)

        # Prepare messages for LLM (last 10 messages for context)
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in context.history[-10:]
        ]

        # Stream response from OpenAI
        stream = await aclient.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            stream=True
        )

        full_response = ""
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                token = chunk.choices[0].delta.content
                full_response += token

                # Send token to client
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

                # Small delay to prevent overwhelming the client
                await asyncio.sleep(0.01)

        # Save assistant response to context
        assistant_msg = Message(
            role="assistant",
            content=full_response,
            timestamp=datetime.now(timezone.utc),
            metadata={
                "streamed": True,
                "agents_used": [r.agent_id for r in routing_decision.agent_responses]
            }
        )
        context.history.append(assistant_msg)

        # Save updated context
        orchestrator.session_store.save(session_id, context)

        # Send completion event
        yield f"data: {json.dumps({
            'type': 'done',
            'message_count': len(context.history),
            'total_tokens': len(full_response.split())
        })}\n\n"

    except Exception as e:
        logger.error(f"Error streaming response: {e}", exc_info=True)
        yield f"data: {json.dumps({
            'type': 'error',
            'message': f'Streaming error: {str(e)}'
        })}\n\n"


@router.post("/stream")
async def stream_message(
    data: StreamMessageRequest,
    current_user: User = Depends(get_current_user),
    _: None = Depends(chat_limiter)
):
    """
    Stream LLM response using Server-Sent Events.

    Returns a stream of events:
    - metadata: Information about which agent is handling the request
    - token: Individual words/tokens as they're generated
    - done: Completion signal with summary

    Example client code (JavaScript):
    ```javascript
    const eventSource = new EventSource('/chat/stream');
    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'token') {
            // Append token to UI
            appendToChat(data.content);
        } else if (data.type === 'done') {
            eventSource.close();
        }
    };
    ```

    Args:
        data: Stream message request
        current_user: Authenticated user

    Returns:
        StreamingResponse with SSE events
    """
    return StreamingResponse(
        stream_agent_response(
            session_id=data.session_id,
            user_message=data.message,
            user_id=str(current_user.id),
            metadata=data.metadata
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


@router.get("/stream-test")
async def stream_test(current_user: User = Depends(get_current_user)):
    """
    Test endpoint for SSE streaming.
    Sends numbers 1-10 with 1 second delays.
    """
    async def generate():
        for i in range(1, 11):
            yield f"data: {json.dumps({'type': 'count', 'value': i})}\n\n"
            await asyncio.sleep(1)
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )
