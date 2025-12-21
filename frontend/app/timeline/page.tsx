"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import Navigation from "@/components/Navigation";
import { getTimeline } from "@/lib/api";

interface TimelineItem {
  id: string;
  session_id: string;
  title: string | null;
  message_count: number;
  agents_used: string[];
  created_at: string;
  updated_at: string | null;
  summary: string | null;
  main_topics: string[];
}

export default function TimelinePage() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const [items, setItems] = useState<TimelineItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
    }
  }, [user, authLoading, router]);

  useEffect(() => {
    if (user) {
      loadTimeline();
    }
  }, [user]);

  const loadTimeline = async () => {
    try {
      const data = await getTimeline();
      // Backend returns array directly, not wrapped in {timeline: []}
      setItems(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Error loading timeline:", error);
    } finally {
      setLoading(false);
    }
  };

  if (authLoading || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-pulse text-primary-600 dark:text-primary-400">
          Ładowanie...
        </div>
      </div>
    );
  }

  return (
    <>
      <Navigation />
      <main className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="max-w-4xl mx-auto px-4 py-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
            Twoja historia rozmów
          </h1>

          {loading ? (
            <div className="text-center text-gray-500 dark:text-gray-400">
              Ładowanie...
            </div>
          ) : items.length === 0 ? (
            <div className="card text-center py-12">
              <svg
                className="w-16 h-16 mx-auto mb-4 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                />
              </svg>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                Brak zapisanych rozmów
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                Rozpocznij swoją pierwszą rozmowę z LifeAI
              </p>
              <button
                onClick={() => router.push("/")}
                className="btn-primary"
              >
                Rozpocznij rozmowę
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {items.map((item) => (
                <div key={item.id} className="card hover:shadow-xl transition-shadow">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                        {item.title || "Rozmowa bez tytułu"}
                      </h3>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        {new Date(item.created_at).toLocaleString("pl-PL", {
                          year: "numeric",
                          month: "long",
                          day: "numeric",
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </p>
                    </div>
                    <span className="text-sm bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300 px-3 py-1 rounded-full">
                      {item.message_count} wiadomości
                    </span>
                  </div>

                  {item.summary && (
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                      {item.summary}
                    </p>
                  )}

                  {item.main_topics && item.main_topics.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {item.main_topics.map((topic, j) => (
                        <span
                          key={j}
                          className="text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-2 py-1 rounded"
                        >
                          {topic}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </>
  );
}
