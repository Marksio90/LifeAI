"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";
import { useAuth } from "@/contexts/AuthContext";
import Navigation from "@/components/Navigation";
import { getProfile, updateProfile, changePassword } from "@/lib/api";

interface Profile {
  id: string;
  email: string;
  username: string | null;
  full_name: string | null;
  preferred_language: string;
  preferred_voice: string;
  is_premium: boolean;
  created_at: string;
  preferences: any;
}

export default function ProfilePage() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{type: "success" | "error", text: string} | null>(null);

  // Profile form
  const [fullName, setFullName] = useState("");
  const [language, setLanguage] = useState("pl");
  const [voice, setVoice] = useState("nova");
  const [autoPlayTTS, setAutoPlayTTS] = useState(false);

  // Password form
  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
    }
  }, [user, authLoading, router]);

  useEffect(() => {
    if (user) {
      loadProfile();
    }
  }, [user]);

  const loadProfile = async () => {
    try {
      const data = await getProfile();
      setProfile(data);
      setFullName(data.full_name || "");
      setLanguage(data.preferred_language || "pl");
      setVoice(data.preferred_voice || "nova");
      setAutoPlayTTS(data.preferences?.auto_play_tts || false);
    } catch (error) {
      console.error("Error loading profile:", error);
      const errorMessage = "Nie udało się załadować profilu";
      setMessage({type: "error", text: errorMessage});
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage(null);

    try {
      await updateProfile({
        full_name: fullName,
        preferred_language: language,
        preferred_voice: voice,
        preferences: {
          auto_play_tts: autoPlayTTS,
        },
      });

      const successMessage = "Profil zaktualizowany pomyślnie!";
      setMessage({type: "success", text: successMessage});
      toast.success(successMessage);
      loadProfile();
    } catch (error: any) {
      const errorMessage = error.message || "Nie udało się zaktualizować profilu";
      setMessage({type: "error", text: errorMessage});
      toast.error(errorMessage);
    } finally {
      setSaving(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();

    if (newPassword !== confirmPassword) {
      const errorMessage = "Nowe hasła nie pasują do siebie";
      setMessage({type: "error", text: errorMessage});
      toast.error(errorMessage);
      return;
    }

    if (newPassword.length < 8) {
      const errorMessage = "Nowe hasło musi mieć co najmniej 8 znaków";
      setMessage({type: "error", text: errorMessage});
      toast.error(errorMessage);
      return;
    }

    setSaving(true);
    setMessage(null);

    try {
      await changePassword({
        current_password: currentPassword,
        new_password: newPassword,
      });

      const successMessage = "Hasło zmienione pomyślnie!";
      setMessage({type: "success", text: successMessage});
      toast.success(successMessage);
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setShowPasswordForm(false);
    } catch (error: any) {
      const errorMessage = error.message || "Nie udało się zmienić hasła";
      setMessage({type: "error", text: errorMessage});
      toast.error(errorMessage);
    } finally {
      setSaving(false);
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

  return (
    <>
      <Navigation />
      <main className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="max-w-4xl mx-auto px-4 py-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
            Twój profil
          </h1>

          {/* Message */}
          {message && (
            <div
              className={`mb-6 p-4 rounded-lg ${
                message.type === "success"
                  ? "bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-300"
                  : "bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-300"
              }`}
            >
              {message.text}
            </div>
          )}

          {/* Account Info */}
          <div className="card mb-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Informacje o koncie
            </h2>
            <dl className="space-y-3">
              <div>
                <dt className="text-sm text-gray-500 dark:text-gray-400">Email</dt>
                <dd className="text-lg font-medium text-gray-900 dark:text-white">{profile?.email}</dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500 dark:text-gray-400">Status konta</dt>
                <dd className="text-lg">
                  <span className={`inline-block px-3 py-1 rounded-full text-sm ${
                    profile?.is_premium
                      ? "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300"
                      : "bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-300"
                  }`}>
                    {profile?.is_premium ? "Premium" : "Free"}
                  </span>
                </dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500 dark:text-gray-400">Data utworzenia</dt>
                <dd className="text-gray-900 dark:text-white">
                  {profile?.created_at && new Date(profile.created_at).toLocaleDateString("pl-PL")}
                </dd>
              </div>
            </dl>
          </div>

          {/* Profile Settings */}
          <form onSubmit={handleUpdateProfile} className="card mb-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Ustawienia profilu
            </h2>

            <div className="space-y-4">
              {/* Full Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Imię i nazwisko
                </label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Jan Kowalski"
                />
              </div>

              {/* Language */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Preferowany język
                </label>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="pl">Polski</option>
                  <option value="en">English</option>
                  <option value="de">Deutsch</option>
                  <option value="es">Español</option>
                  <option value="fr">Français</option>
                </select>
              </div>

              {/* Voice */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Preferowany głos TTS
                </label>
                <select
                  value={voice}
                  onChange={(e) => setVoice(e.target.value)}
                  className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="nova">Nova (żeński)</option>
                  <option value="alloy">Alloy (neutralny)</option>
                  <option value="echo">Echo (męski)</option>
                  <option value="fable">Fable (męski)</option>
                  <option value="onyx">Onyx (męski)</option>
                  <option value="shimmer">Shimmer (żeński)</option>
                </select>
              </div>

              {/* Auto-play TTS */}
              <div className="flex items-center justify-between">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Automatyczne odtwarzanie TTS
                  </label>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Automatycznie odtwarzaj odpowiedzi głosowo
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => setAutoPlayTTS(!autoPlayTTS)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    autoPlayTTS ? "bg-primary-600" : "bg-gray-300 dark:bg-gray-600"
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      autoPlayTTS ? "translate-x-6" : "translate-x-1"
                    }`}
                  />
                </button>
              </div>

              {/* Save Button */}
              <button
                type="submit"
                disabled={saving}
                className="w-full btn-primary"
              >
                {saving ? "Zapisywanie..." : "Zapisz zmiany"}
              </button>
            </div>
          </form>

          {/* Password Change */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Zmiana hasła
            </h2>

            {!showPasswordForm ? (
              <button
                onClick={() => setShowPasswordForm(true)}
                className="btn-secondary"
              >
                Zmień hasło
              </button>
            ) : (
              <form onSubmit={handleChangePassword} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Obecne hasło
                  </label>
                  <input
                    type="password"
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    required
                    className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Nowe hasło
                  </label>
                  <input
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    required
                    minLength={8}
                    className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                  <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                    Minimum 8 znaków
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Potwierdź nowe hasło
                  </label>
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>

                <div className="flex gap-3">
                  <button
                    type="submit"
                    disabled={saving}
                    className="btn-primary flex-1"
                  >
                    {saving ? "Zmiana hasła..." : "Zmień hasło"}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowPasswordForm(false);
                      setCurrentPassword("");
                      setNewPassword("");
                      setConfirmPassword("");
                    }}
                    className="btn-secondary flex-1"
                  >
                    Anuluj
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      </main>
    </>
  );
}
