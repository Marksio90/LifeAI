"use client";

import { motion } from "framer-motion";
import { useState } from "react";

interface MessageBubbleProps {
  role: "user" | "assistant";
  content: string;
  type?: "text" | "voice" | "image";
  imageUrl?: string;
  timestamp?: Date;
  onPlayAudio?: () => void;
  isPlaying?: boolean;
}

export default function MessageBubble({
  role,
  content,
  type = "text",
  imageUrl,
  timestamp,
  onPlayAudio,
  isPlaying = false
}: MessageBubbleProps) {
  const [isHovered, setIsHovered] = useState(false);

  const isUser = role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}
    >
      <div
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        className={`max-w-[70%] group`}
      >
        {/* Message Container */}
        <motion.div
          whileHover={{ scale: 1.02 }}
          transition={{ duration: 0.2 }}
          className={`
            rounded-2xl px-6 py-4 shadow-md
            ${isUser
              ? "bg-gradient-to-br from-primary-600 to-primary-700 text-white"
              : "bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl text-gray-900 dark:text-gray-100 border border-gray-200/50 dark:border-gray-700/50"
            }
            ${isHovered ? "shadow-lg" : "shadow-md"}
            transition-shadow duration-200
          `}
        >
          {/* Image if present */}
          {type === "image" && imageUrl && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1 }}
              className="mb-3"
            >
              <img
                src={imageUrl}
                alt="Uploaded"
                className="max-w-full rounded-lg shadow-sm"
              />
            </motion.div>
          )}

          {/* Voice indicator */}
          {type === "voice" && (
            <div className="flex items-center gap-2 mb-2 opacity-75">
              <motion.svg
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ repeat: Infinity, duration: 1.5 }}
                className="w-4 h-4"
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
              </motion.svg>
              <span className="text-xs">Wiadomość głosowa</span>
            </div>
          )}

          {/* Message content */}
          <p className="whitespace-pre-wrap text-sm sm:text-base leading-relaxed">
            {content}
          </p>

          {/* Timestamp */}
          {timestamp && (
            <div
              className={`
                text-xs mt-2 opacity-60
                ${isUser ? "text-white" : "text-gray-600 dark:text-gray-400"}
              `}
            >
              {timestamp.toLocaleTimeString("pl-PL", {
                hour: "2-digit",
                minute: "2-digit"
              })}
            </div>
          )}
        </motion.div>

        {/* Action buttons (for assistant messages) */}
        {!isUser && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: isHovered ? 1 : 0 }}
            className="flex items-center gap-2 mt-2 ml-4"
          >
            {/* Play audio button */}
            {onPlayAudio && (
              <button
                onClick={onPlayAudio}
                className="
                  flex items-center gap-1 px-3 py-1.5 rounded-lg
                  text-xs
                  bg-gray-100 dark:bg-gray-700
                  hover:bg-gray-200 dark:hover:bg-gray-600
                  text-gray-700 dark:text-gray-300
                  transition-all duration-200
                  hover:scale-105
                "
              >
                {isPlaying ? (
                  <>
                    <svg
                      className="w-3.5 h-3.5"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                    Zatrzymaj
                  </>
                ) : (
                  <>
                    <svg
                      className="w-3.5 h-3.5"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                      />
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                    Odtwórz
                  </>
                )}
              </button>
            )}

            {/* Copy button */}
            <button
              onClick={() => navigator.clipboard.writeText(content)}
              className="
                p-1.5 rounded-lg
                bg-gray-100 dark:bg-gray-700
                hover:bg-gray-200 dark:hover:bg-gray-600
                text-gray-700 dark:text-gray-300
                transition-all duration-200
                hover:scale-105
              "
              title="Kopiuj"
            >
              <svg
                className="w-3.5 h-3.5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                />
              </svg>
            </button>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}
