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
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [daysFilter, setDaysFilter] = useState<number | undefined>(undefined);
  const [sortBy, setSortBy] = useState("created_at");
  const [sortOrder, setSortOrder] = useState("desc");

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
    }
  }, [user, authLoading, router]);

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  useEffect(() => {
    if (user) {
      loadTimeline();
    }
  }, [user, debouncedSearch, daysFilter, sortBy, sortOrder]);

  const loadTimeline = async () => {
    try {
      setLoading(true);
      const data = await getTimeline({
        search: debouncedSearch || undefined,
        days: daysFilter,
        sort_by: sortBy,
        sort_order: sortOrder,
      });

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

          {/* Search and Filters */}
          <div className="mb-6 space-y-4">
            {/* Search bar */}
            <div className="relative">
              <input
                type="text"
                placeholder="Szukaj w rozmowach..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-3 pl-10 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
              <svg
                className="absolute left-3 top-3.5 w-5 h-5 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </div>

            {/* Filters row */}
            <div className="flex flex-wrap gap-3">
              {/* Time filter */}
              <select
                value={daysFilter || "all"}
                onChange={(e) =>
                  setDaysFilter(e.target.value === "all" ? undefined : Number(e.target.value))
                }
                className="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="all">Wszystkie</option>
                <option value="7">Ostatnie 7 dni</option>
                <option value="30">Ostatnie 30 dni</option>
                <option value="90">Ostatnie 90 dni</option>
              </select>

              {/* Sort by */}
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="created_at">Sortuj: Data</option>
                <option value="message_count">Sortuj: Liczba wiadomości</option>
                <option value="title">Sortuj: Tytuł</option>
              </select>

              {/* Sort order */}
              <button
                onClick={() => setSortOrder(sortOrder === "desc" ? "asc" : "desc")}
                className="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white text-sm hover:bg-gray-50 dark:hover:bg-gray-700 focus:ring-2 focus:ring-primary-500"
                title={sortOrder === "desc" ? "Malejąco" : "Rosnąco"}
              >
                {sortOrder === "desc" ? "↓" : "↑"}
              </button>

              {/* Results count */}
              {!loading && (
                <span className="px-4 py-2 text-sm text-gray-600 dark:text-gray-400 flex items-center">
                  Znaleziono: {items.length}
                </span>
              )}
            </div>
          </div>

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
                {debouncedSearch || daysFilter ? (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                ) : (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                  />
                )}
              </svg>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                {debouncedSearch || daysFilter ? "Brak wyników" : "Brak zapisanych rozmów"}
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                {debouncedSearch || daysFilter
                  ? "Spróbuj zmienić kryteria wyszukiwania"
                  : "Rozpocznij swoją pierwszą rozmowę z LifeAI"}
              </p>
              {debouncedSearch || daysFilter ? (
                <button
                  onClick={() => {
                    setSearchQuery("");
                    setDebouncedSearch("");
                    setDaysFilter(undefined);
                  }}
                  className="btn-secondary"
                >
                  Wyczyść filtry
                </button>
              ) : (
                <button onClick={() => router.push("/")} className="btn-primary">
                  Rozpocznij rozmowę
                </button>
              )}
            </div>
          ) : (
            <div className="space-y-4">
              {items.map((item) => (
                <div
                  key={item.id}
                  className="card hover:shadow-xl transition-shadow cursor-pointer"
                  onClick={() => router.push(`/conversation/${item.id}`)}
                >
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
