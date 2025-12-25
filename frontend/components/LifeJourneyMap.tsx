"use client";

import { motion } from "framer-motion";

/**
 * Life Journey Map - Visual Representation of Life Path
 *
 * Shows:
 * - Current life stage
 * - Recent milestones
 * - Upcoming goals
 * - Life transitions
 */

export default function LifeJourneyMap() {
  const lifeStages = [
    { stage: "Childhood", emoji: "👶", active: false },
    { stage: "Adolescence", emoji: "🎓", active: false },
    { stage: "Young Adult", emoji: "🚀", active: true },
    { stage: "Established", emoji: "🏡", active: false },
    { stage: "Wisdom", emoji: "🌟", active: false },
  ];

  const milestones = [
    { title: "Started New Job", date: "2 weeks ago", icon: "💼" },
    { title: "Fitness Goal Achieved", date: "1 month ago", icon: "🏃" },
  ];

  return (
    <div className="bg-white/60 backdrop-blur-lg rounded-3xl p-6 shadow-xl">
      <h3 className="text-xl font-light text-gray-700 mb-4">Life Journey</h3>

      {/* Life Stage Path */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          {lifeStages.map((stage, index) => (
            <motion.div
              key={stage.stage}
              className="flex flex-col items-center"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <motion.div
                className={`w-12 h-12 rounded-full flex items-center justify-center text-2xl ${
                  stage.active
                    ? "bg-gradient-to-br from-purple-400 to-pink-400 shadow-lg"
                    : "bg-gray-200"
                }`}
                animate={
                  stage.active
                    ? {
                        scale: [1, 1.1, 1],
                        boxShadow: [
                          "0 0 20px rgba(168, 85, 247, 0.4)",
                          "0 0 40px rgba(236, 72, 153, 0.4)",
                          "0 0 20px rgba(168, 85, 247, 0.4)",
                        ],
                      }
                    : {}
                }
                transition={{ duration: 2, repeat: Infinity }}
              >
                {stage.emoji}
              </motion.div>
              {index < lifeStages.length - 1 && (
                <div className="w-8 h-0.5 bg-gray-300 mt-6 absolute" style={{ left: "50%" }} />
              )}
            </motion.div>
          ))}
        </div>
        <p className="text-center text-sm text-gray-600 mt-4">Young Adult Stage</p>
      </div>

      {/* Recent Milestones */}
      <div>
        <h4 className="text-sm font-medium text-gray-700 mb-3">Recent Milestones</h4>
        <div className="space-y-2">
          {milestones.map((milestone, index) => (
            <motion.div
              key={milestone.title}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 + index * 0.1 }}
              className="flex items-center gap-3 p-2 bg-white/50 rounded-xl"
            >
              <span className="text-xl">{milestone.icon}</span>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-700">{milestone.title}</p>
                <p className="text-xs text-gray-500">{milestone.date}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className="w-full mt-4 py-2 bg-gradient-to-r from-purple-400 to-pink-400 text-white rounded-xl text-sm font-medium"
      >
        View Full Journey
      </motion.button>
    </div>
  );
}
