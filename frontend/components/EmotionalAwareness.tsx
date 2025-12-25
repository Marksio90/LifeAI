"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";

/**
 * Emotional Awareness Component
 *
 * Shows the AI's emotional intelligence in action:
 * - Detects user's emotional state
 * - Shows empathy and understanding
 * - Adapts communication style
 */

export default function EmotionalAwareness() {
  const [detectedEmotion, setDetectedEmotion] = useState("calm");
  const [empathyMessage, setEmpathyMessage] = useState("I'm here with you");

  const emotions = {
    calm: { emoji: "😌", color: "#60a5fa", message: "I'm here with you" },
    happy: { emoji: "😊", color: "#10b981", message: "I love seeing you happy!" },
    anxious: { emoji: "😰", color: "#f59e0b", message: "Let's work through this together" },
    sad: { emoji: "😔", color: "#8b5cf6", message: "I hear you. You're not alone" },
    excited: { emoji: "🤩", color: "#ec4899", message: "Your energy is contagious!" },
  };

  const currentEmotion = emotions[detectedEmotion as keyof typeof emotions] || emotions.calm;

  return (
    <div className="bg-white/60 backdrop-blur-lg rounded-3xl p-6 shadow-xl">
      <h3 className="text-xl font-light text-gray-700 mb-4">How You're Feeling</h3>

      <AnimatePresence mode="wait">
        <motion.div
          key={detectedEmotion}
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          className="text-center"
        >
          {/* Emotion Orb */}
          <motion.div
            className="relative inline-block mb-4"
            animate={{
              scale: [1, 1.1, 1],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          >
            <div
              className="w-20 h-20 rounded-full flex items-center justify-center text-4xl shadow-lg"
              style={{
                backgroundColor: `${currentEmotion.color}20`,
                boxShadow: `0 0 30px ${currentEmotion.color}40`,
              }}
            >
              {currentEmotion.emoji}
            </div>
          </motion.div>

          <p className="text-gray-700 font-medium mb-2 capitalize">{detectedEmotion}</p>
          <p className="text-sm text-gray-600 italic">&quot;{currentEmotion.message}&quot;</p>
        </motion.div>
      </AnimatePresence>

      {/* Quick Emotion Selectors */}
      <div className="mt-4 flex flex-wrap gap-2 justify-center">
        {Object.keys(emotions).map((emotion) => (
          <motion.button
            key={emotion}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={() => setDetectedEmotion(emotion)}
            className={`text-2xl p-2 rounded-full transition-all ${
              detectedEmotion === emotion ? "bg-white shadow-lg" : "hover:bg-white/50"
            }`}
          >
            {emotions[emotion as keyof typeof emotions].emoji}
          </motion.button>
        ))}
      </div>
    </div>
  );
}
