"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import Navigation from "@/components/Navigation";
import { getConversation, resumeConversation } from "@/lib/api";
import { setResumedConversationId } from "@/lib/session";

interface Message {
  role: string;
  content: string;
  timestamp: string;
  metadata?: any;
}

interface ConversationDetail {
  id: string;
  session_id: string;
  title: string | null;
  language: string;
  messages: Message[];
  message_count: number;
  agents_used: string[];
  created_at: string;
  updated_at: string | null;
  ended_at: string | null;
  summary: string | null;
  main_topics: string[];
}

export default function ConversationPage() {
  const router = useRouter();
  const params = useParams();
  const conversationId = params?.id as string;
  const { user, loading: authLoading } = useAuth();
  const [conversation, setConversation] = useState<ConversationDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [resuming, setResuming] = useState(false);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
    }
  }, [user, authLoading, router]);

  useEffect(() => {
    if (user && conversationId) {
      loadConversation();
    }
  }, [user, conversationId]);

  const loadConversation = async () => {
    try {
      const data = await getConversation(conversationId);
      setConversation(data);
    } catch (error) {
      console.error("Error loading conversation:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleResume = async () => {
    if (!conversationId) return;

    setResuming(true);
    try {
      const response = await resumeConversation(conversationId);
      // Save conversation ID so chat page can load previous messages
      setResumedConversationId(conversationId);
      // Redirect to chat with the new session
      router.push(`/?session=${response.session_id}`);
    } catch (error) {
      console.error("Error resuming conversation:", error);
      alert("Nie udało się wznowić rozmowy");
    } finally {
      setResuming(false);
    }
  };

  if (authLoading || loading || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-pulse text-primary-600 dark:text-primary-400">
          Ładowanie...
        </div>
      </div>
    );
  }

  if (!conversation) {
    return (
      <>
        <Navigation />
        <main className="min-h-screen bg-gray-50 dark:bg-gray-900">
          <div className="max-w-4xl mx-auto px-4 py-8">
            <div className="card text-center py-12">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                Rozmowa nie znaleziona
              </h2>
              <button onClick={() => router.push("/timeline")} className="btn-primary">
                Powrót do historii
              </button>
            </div>
          </div>
        </main>
      </>
    );
  }

  return (
    <>
      <Navigation />
      <main className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="max-w-4xl mx-auto px-4 py-8">
          {/* Header */}
          <div className="mb-6 flex items-start justify-between">
            <div>
              <button
                onClick={() => router.push("/timeline")}
                className="text-primary-600 dark:text-primary-400 hover:underline mb-2 flex items-center gap-2"
              >
                ← Powrót do historii
              </button>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                {conversation.title || "Rozmowa bez tytułu"}
              </h1>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                {new Date(conversation.created_at).toLocaleString("pl-PL", {
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                  hour: "2-digit",
                  minute: "2-digit",
                })}
                {" • "}
                {conversation.message_count} wiadomości
              </p>
            </div>
            <button
              onClick={handleResume}
              disabled={resuming}
              className="btn-primary"
            >
              {resuming ? "Wznawianie..." : "Kontynuuj rozmowę"}
            </button>
          </div>

          {/* Summary */}
          {conversation.summary && (
            <div className="card mb-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Podsumowanie
              </h2>
              <p className="text-gray-600 dark:text-gray-400">{conversation.summary}</p>
            </div>
          )}

          {/* Topics */}
          {conversation.main_topics && conversation.main_topics.length > 0 && (
            <div className="mb-6">
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Główne tematy:
              </h3>
              <div className="flex flex-wrap gap-2">
                {conversation.main_topics.map((topic, i) => (
                  <span
                    key={i}
                    className="text-xs bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300 px-3 py-1 rounded-full"
                  >
                    {topic}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Messages */}
          <div className="space-y-4">
            {conversation.messages.map((message, i) => (
              <div
                key={i}
                className={`card ${
                  message.role === "user"
                    ? "bg-primary-50 dark:bg-primary-900/20"
                    : "bg-white dark:bg-gray-800"
                }`}
              >
                <div className="flex items-start gap-3">
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-semibold ${
                      message.role === "user"
                        ? "bg-primary-600"
                        : "bg-gray-600"
                    }`}
                  >
                    {message.role === "user" ? "U" : "AI"}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                        {message.role === "user" ? "Ty" : "LifeAI"}
                      </span>
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {new Date(message.timestamp).toLocaleTimeString("pl-PL", {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </span>
                    </div>
                    <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                      {message.content}
                    </p>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {message.metadata?.modality && message.metadata.modality !== "text" && (
                        <span className="inline-block text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 px-2 py-1 rounded">
                          {message.metadata.modality === "voice" && "🎤 Wiadomość głosowa"}
                          {message.metadata.modality === "image" && "🖼️ Obraz"}
                        </span>
                      )}
                      {message.metadata?.agent_id && (
                        <span className="inline-block text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 px-2 py-1 rounded">
                          Agent: {message.metadata.agent_id}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </>
  );
}
