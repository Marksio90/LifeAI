"use client";

import { useState, useRef, ChangeEvent } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface AdvancedInputToolbarProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  onVoiceRecord?: () => void;
  onImageUpload?: (file: File) => void;
  onFileUpload?: (file: File) => void;
  isRecording?: boolean;
  disabled?: boolean;
  placeholder?: string;
  maxLength?: number;
}

interface QuickAction {
  id: string;
  label: string;
  icon: React.ReactNode;
  action: () => void;
}

export default function AdvancedInputToolbar({
  value,
  onChange,
  onSend,
  onVoiceRecord,
  onImageUpload,
  onFileUpload,
  isRecording = false,
  disabled = false,
  placeholder = "Wpisz wiadomość...",
  maxLength = 4000,
}: AdvancedInputToolbarProps) {
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const [showQuickActions, setShowQuickActions] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const imageInputRef = useRef<HTMLInputElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Common emojis for quick access
  const commonEmojis = [
    "😊",
    "👍",
    "❤️",
    "🎉",
    "🙏",
    "💪",
    "✨",
    "🔥",
    "💰",
    "🏃",
    "🧘",
    "📊",
    "💼",
    "🎯",
    "⭐",
    "💡",
  ];

  // Quick action templates
  const quickActions: QuickAction[] = [
    {
      id: "summarize",
      label: "Podsumuj rozmowę",
      icon: (
        <svg
          className="w-4 h-4"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
      ),
      action: () => {
        onChange("Proszę podsumuj naszą rozmowę i główne wnioski.");
        setShowQuickActions(false);
      },
    },
    {
      id: "advice",
      label: "Poproś o poradę",
      icon: (
        <svg
          className="w-4 h-4"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
          />
        </svg>
      ),
      action: () => {
        onChange("Jakie masz dla mnie rady w tej sytuacji?");
        setShowQuickActions(false);
      },
    },
    {
      id: "plan",
      label: "Stwórz plan działania",
      icon: (
        <svg
          className="w-4 h-4"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"
          />
        </svg>
      ),
      action: () => {
        onChange("Pomóż mi stworzyć krok po kroku plan działania.");
        setShowQuickActions(false);
      },
    },
    {
      id: "explain",
      label: "Wyjaśnij dokładniej",
      icon: (
        <svg
          className="w-4 h-4"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      ),
      action: () => {
        onChange("Czy możesz to wyjaśnić bardziej szczegółowo?");
        setShowQuickActions(false);
      },
    },
  ];

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Send on Enter (without Shift)
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (value.trim() && !disabled) {
        onSend();
      }
    }
  };

  const handleEmojiClick = (emoji: string) => {
    onChange(value + emoji);
    setShowEmojiPicker(false);
    textareaRef.current?.focus();
  };

  const handleImageUpload = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && onImageUpload) {
      onImageUpload(file);
    }
  };

  const handleFileUpload = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && onFileUpload) {
      onFileUpload(file);
    }
  };

  const formatText = (format: "bold" | "italic" | "code") => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = value.substring(start, end);

    let formattedText = "";
    switch (format) {
      case "bold":
        formattedText = `**${selectedText || "bold text"}**`;
        break;
      case "italic":
        formattedText = `*${selectedText || "italic text"}*`;
        break;
      case "code":
        formattedText = `\`${selectedText || "code"}\``;
        break;
    }

    const newValue =
      value.substring(0, start) + formattedText + value.substring(end);
    onChange(newValue);

    // Restore focus and selection
    setTimeout(() => {
      textarea.focus();
      const newPos = start + formattedText.length;
      textarea.setSelectionRange(newPos, newPos);
    }, 0);
  };

  const charCount = value.length;
  const isNearLimit = charCount > maxLength * 0.9;

  return (
    <div className="relative">
      {/* Toolbar */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className={`
          bg-white dark:bg-gray-800
          border-2 rounded-2xl
          transition-all duration-200
          ${
            isFocused
              ? "border-primary-500 shadow-lg shadow-primary-500/20"
              : "border-gray-200 dark:border-gray-700 shadow-md"
          }
          ${disabled ? "opacity-50 cursor-not-allowed" : ""}
        `}
      >
        {/* Top Toolbar with Format & Actions */}
        <div className="flex items-center gap-1 px-3 py-2 border-b border-gray-200 dark:border-gray-700">
          {/* Formatting Buttons */}
          <div className="flex items-center gap-1">
            <button
              onClick={() => formatText("bold")}
              disabled={disabled}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              title="Bold (Ctrl+B)"
            >
              <svg
                className="w-4 h-4 text-gray-600 dark:text-gray-400"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path d="M6 4v12h4.5c2.485 0 4.5-2.015 4.5-4.5 0-1.313-.563-2.5-1.46-3.33.397-.83.62-1.753.62-2.72C14.16 3.567 12.593 2 10.71 2H6v2zm2 2h2.71c.966 0 1.75.784 1.75 1.75S11.676 9.5 10.71 9.5H8V6zm0 5.5h3.5c1.38 0 2.5 1.12 2.5 2.5S12.88 16.5 11.5 16.5H8v-5z" />
              </svg>
            </button>

            <button
              onClick={() => formatText("italic")}
              disabled={disabled}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              title="Italic (Ctrl+I)"
            >
              <svg
                className="w-4 h-4 text-gray-600 dark:text-gray-400"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path d="M10 4H14V6H11.9L9.1 14H11V16H7V14H9.1L11.9 6H10V4Z" />
              </svg>
            </button>

            <button
              onClick={() => formatText("code")}
              disabled={disabled}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              title="Code"
            >
              <svg
                className="w-4 h-4 text-gray-600 dark:text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"
                />
              </svg>
            </button>
          </div>

          <div className="w-px h-6 bg-gray-300 dark:bg-gray-600 mx-2"></div>

          {/* Emoji Picker Button */}
          <div className="relative">
            <button
              onClick={() => setShowEmojiPicker(!showEmojiPicker)}
              disabled={disabled}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              title="Emoji"
            >
              <svg
                className="w-4 h-4 text-gray-600 dark:text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </button>

            {/* Emoji Picker Popup */}
            <AnimatePresence>
              {showEmojiPicker && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95, y: -10 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95, y: -10 }}
                  className="absolute bottom-full left-0 mb-2 p-3 bg-white dark:bg-gray-800 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 z-50"
                >
                  <div className="grid grid-cols-8 gap-2">
                    {commonEmojis.map((emoji) => (
                      <button
                        key={emoji}
                        onClick={() => handleEmojiClick(emoji)}
                        className="text-xl hover:bg-gray-100 dark:hover:bg-gray-700 rounded p-1 transition-colors"
                      >
                        {emoji}
                      </button>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Quick Actions Button */}
          <div className="relative">
            <button
              onClick={() => setShowQuickActions(!showQuickActions)}
              disabled={disabled}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              title="Quick Actions"
            >
              <svg
                className="w-4 h-4 text-gray-600 dark:text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
            </button>

            {/* Quick Actions Popup */}
            <AnimatePresence>
              {showQuickActions && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95, y: -10 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95, y: -10 }}
                  className="absolute bottom-full left-0 mb-2 w-64 bg-white dark:bg-gray-800 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 z-50"
                >
                  <div className="p-2">
                    {quickActions.map((action) => (
                      <button
                        key={action.id}
                        onClick={action.action}
                        className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors text-left"
                      >
                        <span className="text-primary-600">{action.icon}</span>
                        <span className="text-sm text-gray-700 dark:text-gray-300">
                          {action.label}
                        </span>
                      </button>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Spacer */}
          <div className="flex-1"></div>

          {/* Character Count */}
          {charCount > 0 && (
            <div
              className={`text-xs ${
                isNearLimit ? "text-red-500" : "text-gray-500"
              }`}
            >
              {charCount}/{maxLength}
            </div>
          )}
        </div>

        {/* Text Input Area */}
        <div className="relative">
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            disabled={disabled}
            placeholder={placeholder}
            maxLength={maxLength}
            className="
              w-full px-4 py-3
              bg-transparent
              text-gray-900 dark:text-white
              placeholder-gray-400 dark:placeholder-gray-500
              resize-none
              focus:outline-none
              min-h-[100px]
              max-h-[300px]
            "
            style={{ scrollbarWidth: "thin" }}
          />
        </div>

        {/* Bottom Toolbar with Actions */}
        <div className="flex items-center gap-2 px-3 py-2 border-t border-gray-200 dark:border-gray-700">
          {/* Voice Record Button */}
          {onVoiceRecord && (
            <motion.button
              whileTap={{ scale: 0.95 }}
              onClick={onVoiceRecord}
              disabled={disabled}
              className={`
                p-2 rounded-lg transition-all duration-200
                ${
                  isRecording
                    ? "bg-red-500 text-white animate-pulse"
                    : "hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400"
                }
              `}
              title={isRecording ? "Nagrywanie..." : "Nagraj wiadomość głosową"}
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
                  d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                />
              </svg>
            </motion.button>
          )}

          {/* Image Upload Button */}
          {onImageUpload && (
            <>
              <button
                onClick={() => imageInputRef.current?.click()}
                disabled={disabled}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400 transition-colors"
                title="Wyślij zdjęcie"
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
                    d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
              </button>
              <input
                ref={imageInputRef}
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
                className="hidden"
              />
            </>
          )}

          {/* File Upload Button */}
          {onFileUpload && (
            <>
              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={disabled}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400 transition-colors"
                title="Załącz plik"
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
                    d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"
                  />
                </svg>
              </button>
              <input
                ref={fileInputRef}
                type="file"
                onChange={handleFileUpload}
                className="hidden"
              />
            </>
          )}

          {/* Spacer */}
          <div className="flex-1"></div>

          {/* Send Button */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onSend}
            disabled={disabled || !value.trim()}
            className={`
              px-6 py-2 rounded-xl
              font-medium
              transition-all duration-200
              flex items-center gap-2
              ${
                value.trim() && !disabled
                  ? "bg-primary-600 hover:bg-primary-700 text-white shadow-md hover:shadow-lg"
                  : "bg-gray-200 dark:bg-gray-700 text-gray-400 cursor-not-allowed"
              }
            `}
          >
            <span>Wyślij</span>
            <svg
              className="w-4 h-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
              />
            </svg>
          </motion.button>
        </div>
      </motion.div>

      {/* Hint */}
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="mt-2 text-xs text-gray-500 dark:text-gray-400 text-center"
      >
        Naciśnij <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">Enter</kbd> aby wysłać,{" "}
        <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">Shift+Enter</kbd> dla nowej linii
      </motion.p>
    </div>
  );
}
