"use client";

import { motion } from "framer-motion";
import { useState, useEffect } from "react";

/**
 * Life Pulse - Your Life's Vital Signs
 *
 * Tracks key wellness dimensions:
 * - Physical Health
 * - Mental Clarity
 * - Emotional Balance
 * - Social Connection
 * - Spiritual Alignment
 */

interface VitalSign {
  name: string;
  value: number; // 0-100
  icon: string;
  color: string;
}

export default function LifePulse() {
  const [vitals, setVitals] = useState<VitalSign[]>([
    { name: "Physical", value: 75, icon: "💪", color: "#10b981" },
    { name: "Mental", value: 65, icon: "🧠", color: "#3b82f6" },
    { name: "Emotional", value: 60, icon: "❤️", color: "#ec4899" },
    { name: "Social", value: 70, icon: "👥", color: "#f59e0b" },
    { name: "Spiritual", value: 55, icon: "✨", color: "#8b5cf6" },
  ]);

  return (
    <div className="bg-white/60 backdrop-blur-lg rounded-3xl p-6 shadow-xl">
      <h3 className="text-xl font-light text-gray-700 mb-4">Life Pulse</h3>

      <div className="space-y-3">
        {vitals.map((vital, index) => (
          <motion.div
            key={vital.name}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <span className="text-xl">{vital.icon}</span>
                <span className="text-sm font-medium text-gray-700">{vital.name}</span>
              </div>
              <span className="text-sm font-medium text-gray-600">{vital.value}%</span>
            </div>

            {/* Animated Progress Bar */}
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <motion.div
                className="h-full rounded-full"
                style={{
                  background: `linear-gradient(90deg, ${vital.color}, ${vital.color}dd)`,
                }}
                initial={{ width: 0 }}
                animate={{ width: `${vital.value}%` }}
                transition={{ duration: 1, delay: index * 0.1 }}
              />
            </div>
          </motion.div>
        ))}
      </div>

      {/* Overall Wellness Score */}
      <motion.div
        className="mt-6 pt-6 border-t border-gray-200"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
      >
        <div className="text-center">
          <p className="text-sm text-gray-500 mb-1">Overall Wellness</p>
          <p className="text-3xl font-light text-gray-800">
            {Math.round(vitals.reduce((acc, v) => acc + v.value, 0) / vitals.length)}%
          </p>
        </div>
      </motion.div>
    </div>
  );
}
