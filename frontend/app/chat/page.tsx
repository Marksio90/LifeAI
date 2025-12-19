"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { sendMessage, endChat, transcribeAudio, synthesizeSpeech, analyzeImage } from "@/lib/api";
import { getSessionId, clearSession } from "@/lib/session";
import { useAuth } from "@/contexts/AuthContext";
import Navigation from "@/components/Navigation";
import VoiceRecorder from "@/components/VoiceRecorder";
import ImageUpload from "@/components/ImageUpload";

type MessageType = {
  role: "user" | "assistant";
  content: string;
  type?: "text" | "voice" | "image";
  imageUrl?: string;
};

export default function ChatPage() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const [messages, setMessages] = useState<MessageType[]>([]);
  const [input, setInput] = useState("");
  const sessionId = getSessionId();
  const [isLoading, setIsLoading] = useState(false);
  const [showImageUpload, setShowImageUpload] = useState(false);
  const [playingAudio, setPlayingAudio] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
    }
  }, [user, authLoading, router]);

  useEffect(() => {
    if (!sessionId && !authLoading && user) {
      router.push("/");
    }
  }, [sessionId, authLoading, user, router]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  async function handleSendText() {
    if (!input.trim() || !sessionId || isLoading) return;

    setIsLoading(true);
    const userMessage = input;
    setInput("");

    setMessages((m) => [...m, { role: "user", content: userMessage, type: "text" }]);

    try {
      const res = await sendMessage(sessionId, userMessage);
      setMessages((m) => [...m, { role: "assistant", content: res.reply, type: "text" }]);
    } catch (error) {
      console.error("Error sending message:", error);
      setMessages((m) => [...m, {
        role: "assistant",
        content: "Przepraszam, wystąpił błąd. Spróbuj ponownie.",
        type: "text"
      }]);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleVoiceRecording(audioBlob: Blob) {
    if (!sessionId || isLoading) return;

    setIsLoading(true);

    try {
      // Transcribe audio
      const transcription = await transcribeAudio(audioBlob, user?.preferred_language);
      const userMessage = transcription.text;

      setMessages((m) => [...m, { role: "user", content: userMessage, type: "voice" }]);

      // Send transcribed text to chat
      const res = await sendMessage(sessionId, userMessage);
      setMessages((m) => [...m, { role: "assistant", content: res.reply, type: "text" }]);
    } catch (error) {
      console.error("Error processing voice:", error);
      setMessages((m) => [...m, {
        role: "assistant",
        content: "Nie udało się przetworzyć nagrania głosowego.",
        type: "text"
      }]);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleImageUpload(imageFile: File) {
    if (!sessionId || isLoading) return;

    setIsLoading(true);
    setShowImageUpload(false);

    try {
      // Analyze image
      const analysis = await analyzeImage(imageFile);
      const imageUrl = URL.createObjectURL(imageFile);

      setMessages((m) => [...m, {
        role: "user",
        content: "Przesłano obraz",
        type: "image",
        imageUrl
      }]);

      setMessages((m) => [...m, {
        role: "assistant",
        content: analysis.description || analysis.analysis,
        type: "text"
      }]);
    } catch (error) {
      console.error("Error analyzing image:", error);
      setMessages((m) => [...m, {
        role: "assistant",
        content: "Nie udało się przeanalizować obrazu.",
        type: "text"
      }]);
    } finally {
      setIsLoading(false);
    }
  }

  async function handlePlayAudio(text: string, index: number) {
    if (playingAudio === index) {
      // Stop current audio
      audioRef.current?.pause();
      setPlayingAudio(null);
      return;
    }

    try {
      setPlayingAudio(index);
      const audioBlob = await synthesizeSpeech(text, user?.preferred_voice || 'nova');
      const audioUrl = URL.createObjectURL(audioBlob);

      if (audioRef.current) {
        audioRef.current.pause();
      }

      const audio = new Audio(audioUrl);
      audioRef.current = audio;

      audio.onended = () => {
        setPlayingAudio(null);
      };

      await audio.play();
    } catch (error) {
      console.error("Error playing audio:", error);
      setPlayingAudio(null);
    }
  }

  async function handleEndChat() {
    if (!sessionId) return;

    try {
      await endChat(sessionId);
      clearSession();
      router.push("/timeline");
    } catch (error) {
      console.error("Error ending chat:", error);
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendText();
    }
  };

  if (authLoading || !user || !sessionId) {
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
      <div className="flex flex-col h-screen bg-gray-50 dark:bg-gray-900">
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto px-4 py-6">
          <div className="max-w-4xl mx-auto space-y-4">
            {messages.length === 0 && (
              <div className="text-center text-gray-500 dark:text-gray-400 mt-20">
                <p className="text-lg">Rozpocznij rozmowę...</p>
                <p className="text-sm mt-2">Możesz pisać, mówić lub wysyłać zdjęcia</p>
              </div>
            )}

            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[70%] rounded-lg px-4 py-3 ${
                    msg.role === "user"
                      ? "bg-primary-600 text-white"
                      : "bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 shadow-md"
                  }`}
                >
                  {msg.type === "image" && msg.imageUrl && (
                    <img
                      src={msg.imageUrl}
                      alt="Uploaded"
                      className="max-w-full rounded mb-2"
                    />
                  )}

                  {msg.type === "voice" && (
                    <div className="flex items-center gap-2 mb-1">
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                      </svg>
                      <span className="text-xs opacity-75">Wiadomość głosowa</span>
                    </div>
                  )}

                  <p className="whitespace-pre-wrap">{msg.content}</p>

                  {msg.role === "assistant" && (
                    <button
                      onClick={() => handlePlayAudio(msg.content, i)}
                      className="mt-2 text-xs opacity-75 hover:opacity-100 flex items-center gap-1"
                    >
                      {playingAudio === i ? (
                        <>
                          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          Zatrzymaj
                        </>
                      ) : (
                        <>
                          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          Odtwórz
                        </>
                      )}
                    </button>
                  )}
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white dark:bg-gray-800 rounded-lg px-4 py-3 shadow-md">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Image Upload Modal */}
        {showImageUpload && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Prześlij obraz
                </h3>
                <button
                  onClick={() => setShowImageUpload(false)}
                  className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                >
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <ImageUpload onImageSelect={handleImageUpload} />
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
          <div className="max-w-4xl mx-auto px-4 py-4">
            <div className="flex items-end space-x-3">
              <button
                onClick={() => setShowImageUpload(true)}
                disabled={isLoading}
                className="p-3 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors disabled:opacity-50"
                title="Prześlij obraz"
              >
                <svg className="w-5 h-5 text-gray-600 dark:text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </button>

              <VoiceRecorder
                onRecordingComplete={handleVoiceRecording}
                className="flex-shrink-0"
              />

              <div className="flex-1">
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Napisz wiadomość..."
                  rows={1}
                  className="w-full resize-none input-field"
                  disabled={isLoading}
                />
              </div>

              <button
                onClick={handleSendText}
                disabled={isLoading || !input.trim()}
                className="btn-primary px-6 py-3"
              >
                Wyślij
              </button>

              <button
                onClick={handleEndChat}
                disabled={isLoading}
                className="btn-secondary px-6 py-3"
              >
                Zakończ
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
