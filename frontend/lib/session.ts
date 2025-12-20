const SESSION_KEY = 'lifeai_session_id';

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

export function clearSession(): void {
  if (typeof window !== 'undefined') {
    sessionStorage.removeItem(SESSION_KEY);
  }
}
