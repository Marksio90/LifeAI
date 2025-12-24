"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";

interface Conversation {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: string;
  agentsUsed: string[];
  messageCount: number;
}

interface UserProfile {
  name: string;
  email: string;
  avatar?: string;
  isPremium: boolean;
}

interface Agent {
  id: string;
  name: string;
  status: "active" | "idle";
  color: string;
}

interface ContextSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  currentConversationId?: string;
}

export default function ContextSidebar({
  isOpen,
  onClose,
  currentConversationId,
}: ContextSidebarProps) {
  const [activeTab, setActiveTab] = useState<"conversations" | "agents" | "profile">("conversations");
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isOpen) {
      fetchSidebarData();
    }
  }, [isOpen]);

  const fetchSidebarData = async () => {
    try {
      setLoading(true);

      const token = localStorage.getItem("token");

      // Fetch conversations
      const convResponse = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/chat/conversations`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (convResponse.ok) {
        const convData = await convResponse.json();
        setConversations(convData.slice(0, 10)); // Last 10 conversations
      }

      // Fetch user profile
      const profileResponse = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/user/profile`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (profileResponse.ok) {
        const profileData = await profileResponse.json();
        setUserProfile(profileData);
      }

      // Mock agents data (would come from API in production)
      setAgents([
        { id: "health", name: "Health", status: "active", color: "#10b981" },
        { id: "finance", name: "Finance", status: "active", color: "#6366f1" },
        { id: "relations", name: "Relations", status: "idle", color: "#ec4899" },
        { id: "development", name: "Development", status: "idle", color: "#f59e0b" },
        { id: "tasks", name: "Tasks", status: "idle", color: "#8b5cf6" },
      ]);
    } catch (error) {
      console.error("Error fetching sidebar data:", error);
      // Use mock data
      setConversations(getMockConversations());
      setUserProfile(getMockProfile());
    } finally {
      setLoading(false);
    }
  };

  const getMockConversations = (): Conversation[] => [
    {
      id: "1",
      title: "Budżet domowy na luty",
      lastMessage: "Pomóż mi zaplanować oszczędności...",
      timestamp: "2 godz. temu",
      agentsUsed: ["Finance"],
      messageCount: 12,
    },
    {
      id: "2",
      title: "Plan treningowy",
      lastMessage: "Chcę schudnąć 5 kg...",
      timestamp: "5 godz. temu",
      agentsUsed: ["Health"],
      messageCount: 8,
    },
    {
      id: "3",
      title: "Rozmowa z szefem",
      lastMessage: "Jak się przygotować...",
      timestamp: "wczoraj",
      agentsUsed: ["Relations", "Development"],
      messageCount: 15,
    },
  ];

  const getMockProfile = (): UserProfile => ({
    name: "Jan Kowalski",
    email: "jan@example.com",
    isPremium: true,
  });

  const getAgentBadge = (agentName: string) => {
    const agent = agents.find((a) => a.name === agentName);
    if (!agent) return null;

    return (
      <span
        className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
        style={{
          backgroundColor: `${agent.color}15`,
          color: agent.color,
        }}
      >
        {agentName}
      </span>
    );
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
          />

          {/* Sidebar */}
          <motion.div
            initial={{ x: "-100%" }}
            animate={{ x: 0 }}
            exit={{ x: "-100%" }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="fixed left-0 top-0 bottom-0 w-80 bg-white dark:bg-gray-900 shadow-2xl z-50 flex flex-col"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                Menu
              </h2>
              <button
                onClick={onClose}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              >
                <svg
                  className="w-5 h-5 text-gray-600 dark:text-gray-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>

            {/* User Profile Quick View */}
            {userProfile && (
              <div className="p-4 bg-gradient-to-r from-primary-50 to-purple-50 dark:from-primary-900/20 dark:to-purple-900/20 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-primary-600 flex items-center justify-center text-white font-bold text-lg">
                    {userProfile.name.charAt(0)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-gray-900 dark:text-white truncate">
                      {userProfile.name}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400 truncate">
                      {userProfile.email}
                    </p>
                  </div>
                  {userProfile.isPremium && (
                    <span className="px-2 py-1 bg-yellow-400 text-yellow-900 text-xs font-bold rounded">
                      PRO
                    </span>
                  )}
                </div>
              </div>
            )}

            {/* Tabs */}
            <div className="flex border-b border-gray-200 dark:border-gray-700">
              <button
                onClick={() => setActiveTab("conversations")}
                className={`flex-1 py-3 text-sm font-medium transition-colors ${
                  activeTab === "conversations"
                    ? "text-primary-600 border-b-2 border-primary-600"
                    : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
                }`}
              >
                Rozmowy
              </button>
              <button
                onClick={() => setActiveTab("agents")}
                className={`flex-1 py-3 text-sm font-medium transition-colors ${
                  activeTab === "agents"
                    ? "text-primary-600 border-b-2 border-primary-600"
                    : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
                }`}
              >
                Agenci
              </button>
              <button
                onClick={() => setActiveTab("profile")}
                className={`flex-1 py-3 text-sm font-medium transition-colors ${
                  activeTab === "profile"
                    ? "text-primary-600 border-b-2 border-primary-600"
                    : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
                }`}
              >
                Profil
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto">
              {loading ? (
                <div className="flex items-center justify-center h-full">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                </div>
              ) : (
                <>
                  {/* Conversations Tab */}
                  {activeTab === "conversations" && (
                    <div className="p-2">
                      <div className="mb-4 px-2">
                        <Link
                          href="/chat"
                          className="flex items-center gap-2 px-4 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium transition-colors"
                          onClick={onClose}
                        >
                          <svg
                            className="w-5 h-5"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M12 4v16m8-8H4"
                            />
                          </svg>
                          Nowa rozmowa
                        </Link>
                      </div>

                      {conversations.length === 0 ? (
                        <p className="text-center text-gray-500 dark:text-gray-400 py-8">
                          Brak rozmów
                        </p>
                      ) : (
                        <div className="space-y-2">
                          {conversations.map((conv) => (
                            <Link
                              key={conv.id}
                              href={`/conversation/${conv.id}`}
                              onClick={onClose}
                              className={`block px-3 py-3 rounded-lg transition-all ${
                                conv.id === currentConversationId
                                  ? "bg-primary-50 dark:bg-primary-900/20 border-l-4 border-primary-600"
                                  : "hover:bg-gray-50 dark:hover:bg-gray-800"
                              }`}
                            >
                              <div className="flex items-start justify-between mb-1">
                                <h4 className="font-medium text-gray-900 dark:text-white text-sm truncate flex-1">
                                  {conv.title}
                                </h4>
                                <span className="text-xs text-gray-500 ml-2">
                                  {conv.timestamp}
                                </span>
                              </div>
                              <p className="text-xs text-gray-600 dark:text-gray-400 truncate mb-2">
                                {conv.lastMessage}
                              </p>
                              <div className="flex items-center gap-2">
                                {conv.agentsUsed.map((agent) => (
                                  <span key={agent}>{getAgentBadge(agent)}</span>
                                ))}
                                <span className="text-xs text-gray-500 ml-auto">
                                  {conv.messageCount} msg
                                </span>
                              </div>
                            </Link>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Agents Tab */}
                  {activeTab === "agents" && (
                    <div className="p-4">
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                        Dostępni specjaliści AI
                      </p>
                      <div className="space-y-3">
                        {agents.map((agent) => (
                          <div
                            key={agent.id}
                            className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg"
                          >
                            <div className="flex items-center justify-between mb-2">
                              <div className="flex items-center gap-3">
                                <div
                                  className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold"
                                  style={{ backgroundColor: agent.color }}
                                >
                                  {agent.name.charAt(0)}
                                </div>
                                <div>
                                  <h4 className="font-medium text-gray-900 dark:text-white">
                                    {agent.name}
                                  </h4>
                                  <p className="text-xs text-gray-500">
                                    AI Specialist
                                  </p>
                                </div>
                              </div>
                              <div
                                className={`w-2 h-2 rounded-full ${
                                  agent.status === "active"
                                    ? "bg-green-500"
                                    : "bg-gray-400"
                                }`}
                              />
                            </div>
                            <p className="text-xs text-gray-600 dark:text-gray-400">
                              {agent.status === "active" ? "Aktywny" : "Nieaktywny"}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Profile Tab */}
                  {activeTab === "profile" && userProfile && (
                    <div className="p-4 space-y-4">
                      {/* Quick Links */}
                      <div className="space-y-2">
                        <Link
                          href="/dashboard"
                          onClick={onClose}
                          className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                        >
                          <svg
                            className="w-5 h-5 text-gray-600 dark:text-gray-400"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                            />
                          </svg>
                          <span className="text-gray-900 dark:text-white">
                            Dashboard
                          </span>
                        </Link>

                        <Link
                          href="/profile"
                          onClick={onClose}
                          className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                        >
                          <svg
                            className="w-5 h-5 text-gray-600 dark:text-gray-400"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                            />
                          </svg>
                          <span className="text-gray-900 dark:text-white">
                            Ustawienia profilu
                          </span>
                        </Link>

                        <Link
                          href="/timeline"
                          onClick={onClose}
                          className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                        >
                          <svg
                            className="w-5 h-5 text-gray-600 dark:text-gray-400"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                            />
                          </svg>
                          <span className="text-gray-900 dark:text-white">
                            Historia
                          </span>
                        </Link>

                        <button className="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors text-left">
                          <svg
                            className="w-5 h-5 text-gray-600 dark:text-gray-400"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                            />
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                            />
                          </svg>
                          <span className="text-gray-900 dark:text-white">
                            Ustawienia
                          </span>
                        </button>
                      </div>

                      {/* Logout Button */}
                      <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                        <button
                          onClick={() => {
                            localStorage.removeItem("token");
                            window.location.href = "/login";
                          }}
                          className="w-full flex items-center gap-3 px-4 py-3 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors"
                        >
                          <svg
                            className="w-5 h-5"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                            />
                          </svg>
                          <span className="font-medium">Wyloguj się</span>
                        </button>
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
