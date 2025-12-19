export function getSessionId(): string | null {
  return localStorage.getItem("session_id");
}

export function setSessionId(id: string) {
  localStorage.setItem("session_id", id);
}

export function clearSession() {
  localStorage.removeItem("session_id");
}
