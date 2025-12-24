/**
 * Advanced WebSocket Client for Real-time Chat
 *
 * Features:
 * - Automatic reconnection with exponential backoff
 * - Heartbeat/keepalive
 * - Message queue for offline messages
 * - Streaming message support
 * - Typing indicators
 * - Connection state management
 * - Event-based architecture
 */

import { EventEmitter } from 'events';

export interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

export interface StreamToken {
  message_id: string;
  token: string;
  timestamp: string;
}

export interface ConnectionState {
  status: 'connecting' | 'connected' | 'disconnected' | 'reconnecting';
  lastConnected?: Date;
  reconnectAttempts: number;
}

export class AdvancedWebSocketClient extends EventEmitter {
  private ws: WebSocket | null = null;
  private url: string;
  private token: string;
  private sessionId: string;

  // Connection state
  private state: ConnectionState = {
    status: 'disconnected',
    reconnectAttempts: 0,
  };

  // Reconnection settings
  private reconnectDelay = 1000; // Start with 1 second
  private maxReconnectDelay = 30000; // Max 30 seconds
  private reconnectTimer: NodeJS.Timeout | null = null;

  // Heartbeat settings
  private heartbeatInterval = 30000; // 30 seconds
  private heartbeatTimer: NodeJS.Timeout | null = null;
  private missedHeartbeats = 0;
  private maxMissedHeartbeats = 3;

  // Message queue for offline messages
  private messageQueue: WebSocketMessage[] = [];
  private maxQueueSize = 100;

  // Streaming state
  private streamingMessages: Map<string, string> = new Map();

  constructor(
    baseUrl: string,
    sessionId: string,
    token: string,
    autoConnect = true
  ) {
    super();

    // Build WebSocket URL
    const wsProtocol = baseUrl.startsWith('https') ? 'wss' : 'ws';
    const wsBaseUrl = baseUrl.replace(/^https?:\/\//, '');
    this.url = `${wsProtocol}://${wsBaseUrl}/ws/chat/${sessionId}?token=${token}`;

    this.sessionId = sessionId;
    this.token = token;

    if (autoConnect) {
      this.connect();
    }
  }

  /**
   * Connect to WebSocket server
   */
  public connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      console.log('[WS] Already connected');
      return;
    }

    this.updateState('connecting');
    console.log('[WS] Connecting to:', this.url);

    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = this.handleOpen.bind(this);
      this.ws.onmessage = this.handleMessage.bind(this);
      this.ws.onclose = this.handleClose.bind(this);
      this.ws.onerror = this.handleError.bind(this);
    } catch (error) {
      console.error('[WS] Connection error:', error);
      this.handleReconnect();
    }
  }

  /**
   * Disconnect from WebSocket server
   */
  public disconnect(): void {
    console.log('[WS] Disconnecting...');

    this.stopHeartbeat();
    this.clearReconnectTimer();

    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }

    this.updateState('disconnected');
  }

  /**
   * Send message
   */
  public sendMessage(content: string, messageId?: string): void {
    const message: WebSocketMessage = {
      type: 'message',
      content,
      message_id: messageId || this.generateMessageId(),
      timestamp: new Date().toISOString(),
    };

    this.send(message);
  }

  /**
   * Send typing indicator
   */
  public sendTyping(isTyping: boolean): void {
    this.send({
      type: 'typing',
      is_typing: isTyping,
    });
  }

  /**
   * Send generic message
   */
  private send(message: WebSocketMessage): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      // Queue message if disconnected
      if (this.messageQueue.length < this.maxQueueSize) {
        this.messageQueue.push(message);
        console.log('[WS] Message queued (offline):', message.type);
      } else {
        console.warn('[WS] Message queue full, dropping message');
      }
    }
  }

  /**
   * Get connection state
   */
  public getState(): ConnectionState {
    return { ...this.state };
  }

  /**
   * Check if connected
   */
  public isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  // ========================================================================
  // Private Methods
  // ========================================================================

  private handleOpen(event: Event): void {
    console.log('[WS] Connected successfully');

    this.updateState('connected');
    this.state.lastConnected = new Date();
    this.state.reconnectAttempts = 0;
    this.reconnectDelay = 1000; // Reset delay

    // Start heartbeat
    this.startHeartbeat();

    // Send queued messages
    this.flushMessageQueue();

    // Emit event
    this.emit('connected', event);
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const data = JSON.parse(event.data) as WebSocketMessage;

      // Handle different message types
      switch (data.type) {
        case 'connection_established':
          this.emit('connection_established', data);
          break;

        case 'message_received':
          this.emit('message_ack', data);
          break;

        case 'stream_start':
          this.handleStreamStart(data);
          break;

        case 'stream_token':
          this.handleStreamToken(data);
          break;

        case 'stream_end':
          this.handleStreamEnd(data);
          break;

        case 'stream_error':
          this.handleStreamError(data);
          break;

        case 'heartbeat_ack':
          this.handleHeartbeatAck();
          break;

        case 'error':
          this.emit('error', data);
          break;

        case 'broadcast':
          this.emit('broadcast', data);
          break;

        default:
          this.emit('message', data);
      }
    } catch (error) {
      console.error('[WS] Message parse error:', error);
    }
  }

  private handleClose(event: CloseEvent): void {
    console.log('[WS] Connection closed:', event.code, event.reason);

    this.stopHeartbeat();
    this.ws = null;

    // Emit event
    this.emit('disconnected', {
      code: event.code,
      reason: event.reason,
      wasClean: event.wasClean,
    });

    // Attempt reconnection if not a clean close
    if (!event.wasClean && event.code !== 1000) {
      this.handleReconnect();
    } else {
      this.updateState('disconnected');
    }
  }

  private handleError(event: Event): void {
    console.error('[WS] Error:', event);
    this.emit('error', event);
  }

  private handleReconnect(): void {
    this.updateState('reconnecting');

    this.clearReconnectTimer();

    // Exponential backoff
    const delay = Math.min(
      this.reconnectDelay * Math.pow(2, this.state.reconnectAttempts),
      this.maxReconnectDelay
    );

    console.log(
      `[WS] Reconnecting in ${delay}ms (attempt ${
        this.state.reconnectAttempts + 1
      })...`
    );

    this.reconnectTimer = setTimeout(() => {
      this.state.reconnectAttempts++;
      this.connect();
    }, delay);
  }

  private clearReconnectTimer(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  private startHeartbeat(): void {
    this.stopHeartbeat();

    this.heartbeatTimer = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        // Send heartbeat
        this.send({ type: 'heartbeat' });

        // Check missed heartbeats
        this.missedHeartbeats++;

        if (this.missedHeartbeats > this.maxMissedHeartbeats) {
          console.warn('[WS] Too many missed heartbeats, reconnecting...');
          this.ws.close(1006, 'Heartbeat timeout');
        }
      }
    }, this.heartbeatInterval);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
    this.missedHeartbeats = 0;
  }

  private handleHeartbeatAck(): void {
    this.missedHeartbeats = 0;
  }

  private flushMessageQueue(): void {
    if (this.messageQueue.length === 0) return;

    console.log(`[WS] Flushing ${this.messageQueue.length} queued messages`);

    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      if (message) {
        this.send(message);
      }
    }
  }

  private handleStreamStart(data: any): void {
    const messageId = data.message_id;
    this.streamingMessages.set(messageId, '');

    this.emit('stream_start', {
      messageId,
      timestamp: data.timestamp,
    });
  }

  private handleStreamToken(data: any): void {
    const messageId = data.message_id;
    const token = data.token;

    // Append token to streaming message
    const current = this.streamingMessages.get(messageId) || '';
    this.streamingMessages.set(messageId, current + token);

    this.emit('stream_token', {
      messageId,
      token,
      fullText: this.streamingMessages.get(messageId),
      timestamp: data.timestamp,
    });
  }

  private handleStreamEnd(data: any): void {
    const messageId = data.message_id;
    const fullResponse = data.full_response;

    this.emit('stream_end', {
      messageId,
      fullResponse,
      timestamp: data.timestamp,
    });

    // Cleanup
    this.streamingMessages.delete(messageId);
  }

  private handleStreamError(data: any): void {
    const messageId = data.message_id;

    this.emit('stream_error', {
      messageId,
      error: data.error,
      timestamp: data.timestamp,
    });

    // Cleanup
    this.streamingMessages.delete(messageId);
  }

  private updateState(
    status: 'connecting' | 'connected' | 'disconnected' | 'reconnecting'
  ): void {
    this.state.status = status;
    this.emit('state_change', this.state);
  }

  private generateMessageId(): string {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

/**
 * React hook for WebSocket client
 */
export function useWebSocket(
  baseUrl: string,
  sessionId: string,
  token: string
) {
  // Implementation would go here for React integration
  // This is just a placeholder showing the API
  return {
    client: null as AdvancedWebSocketClient | null,
    isConnected: false,
    state: {} as ConnectionState,
    sendMessage: (content: string) => {},
    sendTyping: (isTyping: boolean) => {},
  };
}

export default AdvancedWebSocketClient;
