"use client";

import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import Navigation from "@/components/Navigation";
import { startChat } from "../lib/api";
import { setSessionId } from "../lib/session";

export default function Home() {
  const router = useRouter();
  const { user, loading } = useAuth();

  async function handleStart() {
    const data = await startChat();
    setSessionId(data.session_id);
    router.push("/chat");
  }

  if (loading) {
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
      <main className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-primary-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center">
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6">
              Masz chaos w głowie?
            </h1>
            <p className="text-xl md:text-2xl text-gray-600 dark:text-gray-300 mb-12 max-w-3xl mx-auto">
              Zatrzymajmy się i poukładajmy to razem. LifeAI to wieloagentowa platforma AI wspierająca Cię w życiu codziennym.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
              {user ? (
                <button
                  onClick={handleStart}
                  className="btn-primary text-lg px-8 py-4 shadow-lg hover:shadow-xl transition-shadow"
                >
                  Rozpocznij rozmowę
                </button>
              ) : (
                <>
                  <button
                    onClick={() => router.push("/register")}
                    className="btn-primary text-lg px-8 py-4 shadow-lg hover:shadow-xl transition-shadow"
                  >
                    Zacznij za darmo
                  </button>
                  <button
                    onClick={() => router.push("/login")}
                    className="btn-secondary text-lg px-8 py-4"
                  >
                    Mam już konto
                  </button>
                </>
              )}
            </div>

            {/* Features Grid */}
            <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto mt-20">
              <div className="card text-center">
                <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <svg className="w-6 h-6 text-primary-600 dark:text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  Rozmowa tekstowa
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Czatuj z AI w sposób naturalny i intuicyjny
                </p>
              </div>

              <div className="card text-center">
                <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <svg className="w-6 h-6 text-primary-600 dark:text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  Komunikacja głosowa
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Rozmawiaj głosowo w ponad 100 językach
                </p>
              </div>

              <div className="card text-center">
                <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <svg className="w-6 h-6 text-primary-600 dark:text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  Analiza obrazów
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Wysyłaj zdjęcia i otrzymuj inteligentną analizę
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}
