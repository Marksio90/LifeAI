"use client";

import { motion } from "framer-motion";
import { useState, useEffect } from "react";

interface WellnessOrbProps {
  mood: number; // 0-10
  onMoodChange?: (mood: number) => void;
}

/**
 * Wellness Orb - The Beating Heart of the Platform
 *
 * A living, breathing orb that:
 * - Pulses like a heartbeat
 * - Changes color based on emotional state
 * - Provides ambient emotional awareness
 * - Invites interaction through its aliveness
 */

export default function WellnessOrb({ mood, onMoodChange }: WellnessOrbProps) {
  const [isHovering, setIsHovering] = useState(false);

  // Color based on mood
  const getOrbColor = (mood: number) => {
    if (mood >= 8) return ["#10b981", "#34d399", "#6ee7b7"]; // Green - Thriving
    if (mood >= 6) return ["#3b82f6", "#60a5fa", "#93c5fd"]; // Blue - Good
    if (mood >= 4) return ["#f59e0b", "#fbbf24", "#fcd34d"]; // Yellow - Okay
    if (mood >= 2) return ["#f97316", "#fb923c", "#fdba74"]; // Orange - Struggling
    return ["#ef4444", "#f87171", "#fca5a5"]; // Red - Very difficult
  };

  const [colors, setColors] = useState(getOrbColor(mood));

  useEffect(() => {
    setColors(getOrbColor(mood));
  }, [mood]);

  return (
    <div className="relative">
      <div className="bg-white/60 backdrop-blur-lg rounded-3xl p-8 shadow-xl">
        <h3 className="text-xl font-light text-gray-700 mb-6 text-center">Your Wellness</h3>

        {/* The Orb */}
        <div className="flex justify-center items-center mb-6">
          <motion.div
            className="relative w-48 h-48 cursor-pointer"
            onHoverStart={() => setIsHovering(true)}
            onHoverEnd={() => setIsHovering(false)}
            whileHover={{ scale: 1.05 }}
          >
            {/* Pulsing rings */}
            {[0, 1, 2].map((i) => (
              <motion.div
                key={i}
                className="absolute inset-0 rounded-full"
                style={{
                  background: `radial-gradient(circle, ${colors[0]}40, ${colors[1]}20, transparent)`,
                }}
                animate={{
                  scale: [1, 1.2, 1],
                  opacity: [0.6, 0.2, 0.6],
                }}
                transition={{
                  duration: 3,
                  repeat: Infinity,
                  delay: i * 0.5,
                  ease: "easeInOut",
                }}
              />
            ))}

            {/* Core orb */}
            <motion.div
              className="absolute inset-4 rounded-full shadow-2xl"
              style={{
                background: `radial-gradient(circle at 30% 30%, ${colors[2]}, ${colors[1]}, ${colors[0]})`,
              }}
              animate={{
                boxShadow: [
                  `0 0 20px ${colors[0]}80`,
                  `0 0 40px ${colors[1]}80`,
                  `0 0 20px ${colors[0]}80`,
                ],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: "easeInOut",
              }}
            >
              {/* Breathing effect */}
              <motion.div
                className="absolute inset-0 rounded-full"
                style={{
                  background: `radial-gradient(circle at 60% 60%, transparent 40%, ${colors[0]}40)`,
                }}
                animate={{
                  scale: [1, 1.1, 1],
                  opacity: [0.5, 0.8, 0.5],
                }}
                transition={{
                  duration: 4,
                  repeat: Infinity,
                  ease: "easeInOut",
                }}
              />

              {/* Mood indicator */}
              <div className="absolute inset-0 flex items-center justify-center">
                <motion.div
                  className="text-white text-4xl font-light"
                  animate={{
                    scale: isHovering ? [1, 1.2, 1] : 1,
                  }}
                  transition={{
                    duration: 0.5,
                    repeat: isHovering ? Infinity : 0,
                  }}
                >
                  {mood >= 8 && "😊"}
                  {mood >= 6 && mood < 8 && "🙂"}
                  {mood >= 4 && mood < 6 && "😐"}
                  {mood >= 2 && mood < 4 && "😔"}
                  {mood < 2 && "😞"}
                </motion.div>
              </div>
            </motion.div>
          </motion.div>
        </div>

        {/* Mood Description */}
        <div className="text-center mb-4">
          <p className="text-2xl font-light text-gray-800">
            {mood >= 8 && "Thriving"}
            {mood >= 6 && mood < 8 && "Doing Well"}
            {mood >= 4 && mood < 6 && "Managing"}
            {mood >= 2 && mood < 4 && "Struggling"}
            {mood < 2 && "Need Support"}
          </p>
          <p className="text-sm text-gray-500 mt-1">
            {mood >= 8 && "You're feeling great today!"}
            {mood >= 6 && mood < 8 && "Things are going pretty well"}
            {mood >= 4 && mood < 6 && "You're doing okay"}
            {mood >= 2 && mood < 4 && "It's been tough lately"}
            {mood < 2 && "I'm here for you"}
          </p>
        </div>

        {/* Quick Actions */}
        <div className="flex gap-2 justify-center">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="px-4 py-2 bg-white/80 rounded-xl text-sm text-gray-700 hover:bg-white transition-all"
          >
            Talk About It
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="px-4 py-2 bg-white/80 rounded-xl text-sm text-gray-700 hover:bg-white transition-all"
          >
            Daily Reflection
          </motion.button>
        </div>
      </div>
    </div>
  );
}
