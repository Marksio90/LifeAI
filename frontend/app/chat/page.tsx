"use client";

import { useEffect, useState } from "react";
import { sendMessage, endChat } from "../../lib/api";
import { getSessionId, clearSession } from "../../lib/session";

type Msg = { role: "user" | "assistant"; content: string };

export default function ChatPage() {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const sessionId = getSessionId();
  const [isLoading, setIsLoading] = useState(false);

  async function handleSend() {
  if (!input || !sessionId || isLoading) return;

  setIsLoading(true);

  setMessages((m) => [...m, { role: "user", content: input }]);
  setInput("");

  try {
    const res = await sendMessage(sessionId, input);
    setMessages((m) => [...m, { role: "assistant", content: res.reply }]);
  } finally {
    setIsLoading(false);
  }
}

  async function handleEnd() {
    if (!sessionId) return;
    await endChat(sessionId);
    clearSession();
    window.location.href = "/timeline";
  }

  return (
    <main style={{ padding: 40 }}>
      <div>
        {messages.map((m, i) => (
          <div key={i}>
            <b>{m.role === "user" ? "Ty" : "AI"}:</b> {m.content}
          </div>
        ))}
      </div>

      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Napisz, co masz w głowie..."
      />
      <button onClick={handleSend} disabled={isLoading || !input}>
        {isLoading ? "AI myśli…" : "Wyślij"}
      </button>
      <button onClick={handleEnd} disabled={isLoading}>
        Zakończ
      </button>
    </main>
  );
}
