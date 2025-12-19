"use client";

import { useRouter } from "next/navigation";
import { startChat } from "../lib/api";
import { setSessionId } from "../lib/session";

export default function Home() {
  const router = useRouter();

  async function handleStart() {
    const data = await startChat();
    setSessionId(data.session_id);
    router.push("/chat");
  }

  return (
    <main style={{ padding: 40 }}>
      <h1>Masz chaos w głowie?</h1>
      <p>Zatrzymajmy się i poukładajmy to razem.</p>
      <button onClick={handleStart}>Zaczynam</button>
    </main>
  );
}
