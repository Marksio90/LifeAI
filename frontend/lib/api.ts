const API_URL = process.env.NEXT_PUBLIC_API_URL!;

export async function startChat() {
  const res = await fetch(`${API_URL}/chat/start`, { method: "POST" });
  return res.json();
}

export async function sendMessage(sessionId: string, message: string) {
  const res = await fetch(`${API_URL}/chat/message`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      message,
    }),
  });
  return res.json();
}

export async function endChat(sessionId: string) {
  const res = await fetch(`${API_URL}/chat/end?session_id=${sessionId}`, {
    method: "POST",
  });
  return res.json();
}

export async function getTimeline() {
  const res = await fetch(`${API_URL}/timeline/`);
  return res.json();
}
