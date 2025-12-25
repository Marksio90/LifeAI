"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import WellnessOrb from "@/components/WellnessOrb";
import LifePulse from "@/components/LifePulse";
import EmotionalAwareness from "@/components/EmotionalAwareness";
import DailyRituals from "@/components/DailyRituals";
import LifeJourneyMap from "@/components/LifeJourneyMap";
import ConversationFlow from "@/components/ConversationFlow";

/**
 * Companion Page - The Living, Breathing Interface
 *
 * This is NOT a chatbot. This is a living companion that:
 * - Breathes and pulses with life
 * - Senses and responds to emotions
 * - Adapts to your life stage and context
 * - Feels warm, organic, and alive
 */

export default function CompanionPage() {
  const [userMood, setUserMood] = useState<number>(5); // 0-10 scale
  const [timeOfDay, setTimeOfDay] = useState<"morning" | "day" | "evening" | "night">("day");
  const [showCheckin, setShowCheckin] = useState(false);

  useEffect(() => {
    // Detect time of day
    const hour = new Date().getHours();
    if (hour >= 5 && hour < 12) setTimeOfDay("morning");
    else if (hour >= 12 && hour < 17) setTimeOfDay("day");
    else if (hour >= 17 && hour < 22) setTimeOfDay("evening");
    else setTimeOfDay("night");

    // Show daily check-in if not done today
    const lastCheckin = localStorage.getItem("last_checkin");
    const today = new Date().toDateString();
    if (lastCheckin !== today) {
      setTimeout(() => setShowCheckin(true), 2000);
    }
  }, []);

  // Dynamic background based on time of day and mood
  const getBackgroundGradient = () => {
    const moodColor = userMood > 7 ? "from-amber-50" : userMood > 4 ? "from-blue-50" : "from-purple-50";

    switch (timeOfDay) {
      case "morning":
        return `${moodColor} via-orange-50 to-yellow-50`;
      case "day":
        return `${moodColor} via-sky-50 to-blue-50`;
      case "evening":
        return `${moodColor} via-purple-50 to-indigo-50`;
      case "night":
        return `${moodColor} via-indigo-900 to-purple-900`;
    }
  };

  return (
    <div className={`min-h-screen bg-gradient-to-br ${getBackgroundGradient()} transition-all duration-1000`}>
      {/* Living Background Animation */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute inset-0"
          animate={{
            background: [
              "radial-gradient(circle at 20% 50%, rgba(255,255,255,0.1) 0%, transparent 50%)",
              "radial-gradient(circle at 80% 50%, rgba(255,255,255,0.1) 0%, transparent 50%)",
              "radial-gradient(circle at 50% 80%, rgba(255,255,255,0.1) 0%, transparent 50%)",
              "radial-gradient(circle at 20% 50%, rgba(255,255,255,0.1) 0%, transparent 50%)",
            ],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 py-8">
        {/* Header with Time-Based Greeting */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl md:text-5xl font-light text-gray-800 mb-2">
            {timeOfDay === "morning" && "Good Morning ☀️"}
            {timeOfDay === "day" && "Hello 🌤️"}
            {timeOfDay === "evening" && "Good Evening 🌅"}
            {timeOfDay === "night" && "Good Night 🌙"}
          </h1>
          <p className="text-lg text-gray-600">How can I support you today?</p>
        </motion.div>

        {/* Main Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Wellness & Awareness */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="space-y-6"
          >
            {/* Wellness Orb - The Heart of the System */}
            <WellnessOrb mood={userMood} onMoodChange={setUserMood} />

            {/* Emotional Awareness */}
            <EmotionalAwareness />

            {/* Life Pulse - Vitals */}
            <LifePulse />
          </motion.div>

          {/* Center Column: Conversation */}
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="lg:col-span-1"
          >
            <ConversationFlow mood={userMood} timeOfDay={timeOfDay} />
          </motion.div>

          {/* Right Column: Life Journey & Rituals */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
            className="space-y-6"
          >
            {/* Daily Rituals */}
            <DailyRituals timeOfDay={timeOfDay} />

            {/* Life Journey Map */}
            <LifeJourneyMap />
          </motion.div>
        </div>

        {/* Daily Check-in Modal */}
        <AnimatePresence>
          {showCheckin && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
              onClick={() => setShowCheckin(false)}
            >
              <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.8, opacity: 0 }}
                className="bg-white rounded-3xl p-8 max-w-md shadow-2xl"
                onClick={(e) => e.stopPropagation()}
              >
                <h2 className="text-2xl font-light text-gray-800 mb-4">
                  {timeOfDay === "morning" ? "Morning Check-in" : "Daily Check-in"}
                </h2>
                <p className="text-gray-600 mb-6">How are you feeling right now?</p>

                {/* Mood Slider */}
                <div className="mb-6">
                  <input
                    type="range"
                    min="0"
                    max="10"
                    value={userMood}
                    onChange={(e) => setUserMood(parseInt(e.target.value))}
                    className="w-full h-2 bg-gradient-to-r from-red-400 via-yellow-400 to-green-400 rounded-lg appearance-none cursor-pointer"
                  />
                  <div className="flex justify-between text-sm text-gray-500 mt-2">
                    <span>Struggling</span>
                    <span>Okay</span>
                    <span>Thriving</span>
                  </div>
                </div>

                <button
                  onClick={() => {
                    localStorage.setItem("last_checkin", new Date().toDateString());
                    setShowCheckin(false);
                  }}
                  className="w-full py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-xl font-medium hover:shadow-lg transition-all"
                >
                  Continue
                </button>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
