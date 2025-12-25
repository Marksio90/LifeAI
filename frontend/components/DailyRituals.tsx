"use client";

import { motion } from "framer-motion";
import { useState } from "react";

interface DailyRitualsProps {
  timeOfDay: "morning" | "day" | "evening" | "night";
}

/**
 * Daily Rituals - Building Meaningful Routines
 *
 * Helps users establish and maintain daily rituals for wellbeing.
 */

export default function DailyRituals({ timeOfDay }: DailyRitualsProps) {
  const rituals = {
    morning: [
      { name: "Morning Intention", icon: "🌅", completed: false },
      { name: "Gratitude Practice", icon: "🙏", completed: true },
      { name: "Energy Check", icon: "⚡", completed: false },
    ],
    day: [
      { name: "Midday Pause", icon: "☕", completed: false },
      { name: "Progress Review", icon: "📊", completed: false },
    ],
    evening: [
      { name: "Day Reflection", icon: "🌆", completed: false },
      { name: "Celebrate Wins", icon: "🎉", completed: false },
      { name: "Tomorrow Planning", icon: "📝", completed: false },
    ],
    night: [
      { name: "Wind Down", icon: "🌙", completed: false },
      { name: "Sleep Prep", icon: "😴", completed: false },
    ],
  };

  const currentRituals = rituals[timeOfDay];
  const [ritualStates, setRitualStates] = useState(currentRituals);

  const toggleRitual = (index: number) => {
    const newStates = [...ritualStates];
    newStates[index].completed = !newStates[index].completed;
    setRitualStates(newStates);
  };

  return (
    <div className="bg-white/60 backdrop-blur-lg rounded-3xl p-6 shadow-xl">
      <h3 className="text-xl font-light text-gray-700 mb-4">
        {timeOfDay.charAt(0).toUpperCase() + timeOfDay.slice(1)} Rituals
      </h3>

      <div className="space-y-3">
        {ritualStates.map((ritual, index) => (
          <motion.div
            key={ritual.name}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`flex items-center gap-3 p-3 rounded-xl cursor-pointer transition-all ${
              ritual.completed ? "bg-green-100/50" : "bg-white/50 hover:bg-white"
            }`}
            onClick={() => toggleRitual(index)}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <motion.div
              className="text-2xl"
              animate={{
                rotate: ritual.completed ? [0, 10, -10, 0] : 0,
              }}
              transition={{ duration: 0.5 }}
            >
              {ritual.icon}
            </motion.div>

            <div className="flex-1">
              <p
                className={`text-sm font-medium ${
                  ritual.completed ? "text-green-700 line-through" : "text-gray-700"
                }`}
              >
                {ritual.name}
              </p>
            </div>

            <div
              className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                ritual.completed ? "bg-green-500 border-green-500" : "border-gray-300"
              }`}
            >
              {ritual.completed && (
                <motion.svg
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="w-3 h-3 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </motion.svg>
              )}
            </div>
          </motion.div>
        ))}
      </div>

      <motion.div
        className="mt-4 text-center text-sm text-gray-500"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        {ritualStates.filter((r) => r.completed).length} of {ritualStates.length} completed
      </motion.div>
    </div>
  );
}
