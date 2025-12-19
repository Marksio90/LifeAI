"use client";

import { useEffect, useState } from "react";
import { getTimeline } from "../../lib/api";

export default function TimelinePage() {
  const [items, setItems] = useState<any[]>([]);

  useEffect(() => {
    getTimeline().then((data) => setItems(data.timeline || []));
  }, []);

  return (
    <main style={{ padding: 40 }}>
      <h2>Twoja historia</h2>
      {items.length === 0 && <p>Brak zapisanych rozmów.</p>}
      {items.map((item, i) => (
        <div key={i}>
          <strong>{item.summary}</strong>
        </div>
      ))}
    </main>
  );
}
