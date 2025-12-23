const SESSION_KEY = 'lifeai_session_id';
const CONVERSATION_KEY = 'lifeai_resumed_conversation_id';

export function setSessionId(sessionId: string): void {
  if (typeof window !== 'undefined') {
    sessionStorage.setItem(SESSION_KEY, sessionId);
  }
}

export function getSessionId(): string | null {
  if (typeof window !== 'undefined') {
    return sessionStorage.getItem(SESSION_KEY);
  }
  return null;
}

export function setResumedConversationId(conversationId: string): void {
  if (typeof window !== 'undefined') {
    sessionStorage.setItem(CONVERSATION_KEY, conversationId);
  }
}

export function getResumedConversationId(): string | null {
  if (typeof window !== 'undefined') {
    return sessionStorage.getItem(CONVERSATION_KEY);
  }
  return null;
}

export function clearResumedConversationId(): void {
  if (typeof window !== 'undefined') {
    sessionStorage.removeItem(CONVERSATION_KEY);
  }
}

export function clearSession(): void {
  if (typeof window !== 'undefined') {
    sessionStorage.removeItem(SESSION_KEY);
    sessionStorage.removeItem(CONVERSATION_KEY);
  }
}
