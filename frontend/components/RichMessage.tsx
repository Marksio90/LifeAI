"use client";

import { motion } from "framer-motion";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

// Rich message type definitions
export type RichMessageType =
  | "text"
  | "card"
  | "list"
  | "chart"
  | "action-buttons"
  | "progress"
  | "table"
  | "alert";

export interface ChartData {
  type: "line" | "bar" | "pie";
  data: any[];
  xKey?: string;
  yKey?: string;
  colors?: string[];
}

export interface CardData {
  title: string;
  subtitle?: string;
  description: string;
  image?: string;
  footer?: string;
  actions?: ActionButton[];
}

export interface ActionButton {
  label: string;
  action: string;
  variant?: "primary" | "secondary" | "danger";
}

export interface ListItem {
  icon?: string;
  title: string;
  description?: string;
  checked?: boolean;
}

export interface TableData {
  headers: string[];
  rows: string[][];
}

export interface ProgressData {
  label: string;
  value: number;
  max: number;
  color?: string;
}

export interface RichMessageData {
  type: RichMessageType;
  content?: string;
  data?: ChartData | CardData | ListItem[] | TableData | ProgressData | ActionButton[];
}

interface RichMessageProps {
  message: RichMessageData;
  onAction?: (action: string) => void;
}

export default function RichMessage({ message, onAction }: RichMessageProps) {
  const renderContent = () => {
    switch (message.type) {
      case "text":
        return <TextMessage content={message.content || ""} />;

      case "card":
        return (
          <CardMessage
            data={message.data as CardData}
            onAction={onAction}
          />
        );

      case "list":
        return <ListMessage items={message.data as ListItem[]} />;

      case "chart":
        return <ChartMessage data={message.data as ChartData} />;

      case "action-buttons":
        return (
          <ActionButtonsMessage
            buttons={message.data as ActionButton[]}
            onAction={onAction}
          />
        );

      case "progress":
        return <ProgressMessage data={message.data as ProgressData} />;

      case "table":
        return <TableMessage data={message.data as TableData} />;

      case "alert":
        return <AlertMessage content={message.content || ""} />;

      default:
        return <TextMessage content={message.content || ""} />;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {renderContent()}
    </motion.div>
  );
}

// Text Message Component
function TextMessage({ content }: { content: string }) {
  return (
    <div className="prose dark:prose-invert max-w-none">
      <p className="whitespace-pre-wrap leading-relaxed">{content}</p>
    </div>
  );
}

// Card Message Component
function CardMessage({
  data,
  onAction,
}: {
  data: CardData;
  onAction?: (action: string) => void;
}) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm">
      {data.image && (
        <img
          src={data.image}
          alt={data.title}
          className="w-full h-48 object-cover"
        />
      )}
      <div className="p-5">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
          {data.title}
        </h3>
        {data.subtitle && (
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
            {data.subtitle}
          </p>
        )}
        <p className="text-gray-700 dark:text-gray-300 mb-4">
          {data.description}
        </p>
        {data.footer && (
          <p className="text-sm text-gray-500 dark:text-gray-400 border-t border-gray-200 dark:border-gray-700 pt-3">
            {data.footer}
          </p>
        )}
        {data.actions && data.actions.length > 0 && (
          <div className="flex gap-2 mt-4">
            {data.actions.map((action, index) => (
              <button
                key={index}
                onClick={() => onAction?.(action.action)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  action.variant === "primary"
                    ? "bg-primary-600 hover:bg-primary-700 text-white"
                    : action.variant === "danger"
                    ? "bg-red-600 hover:bg-red-700 text-white"
                    : "bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-900 dark:text-white"
                }`}
              >
                {action.label}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// List Message Component
function ListMessage({ items }: { items: ListItem[] }) {
  return (
    <ul className="space-y-3">
      {items.map((item, index) => (
        <motion.li
          key={index}
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: index * 0.1 }}
          className="flex items-start gap-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
        >
          {item.icon && <span className="text-2xl">{item.icon}</span>}
          {item.checked !== undefined && (
            <span className="text-xl">
              {item.checked ? "✅" : "⬜"}
            </span>
          )}
          <div className="flex-1">
            <h4 className="font-medium text-gray-900 dark:text-white">
              {item.title}
            </h4>
            {item.description && (
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                {item.description}
              </p>
            )}
          </div>
        </motion.li>
      ))}
    </ul>
  );
}

// Chart Message Component
function ChartMessage({ data }: { data: ChartData }) {
  const COLORS = ["#6366f1", "#8b5cf6", "#ec4899", "#f59e0b", "#10b981"];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-5 border border-gray-200 dark:border-gray-700">
      <ResponsiveContainer width="100%" height={300}>
        {data.type === "line" && (
          <LineChart data={data.data}>
            <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
            <XAxis dataKey={data.xKey || "name"} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey={data.yKey || "value"}
              stroke={data.colors?.[0] || COLORS[0]}
              strokeWidth={3}
              dot={{ r: 5 }}
              activeDot={{ r: 7 }}
            />
          </LineChart>
        )}

        {data.type === "bar" && (
          <BarChart data={data.data}>
            <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
            <XAxis dataKey={data.xKey || "name"} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar
              dataKey={data.yKey || "value"}
              fill={data.colors?.[0] || COLORS[0]}
              radius={[8, 8, 0, 0]}
            />
          </BarChart>
        )}

        {data.type === "pie" && (
          <PieChart>
            <Pie
              data={data.data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) =>
                `${name}: ${(percent * 100).toFixed(0)}%`
              }
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
            >
              {data.data.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={data.colors?.[index] || COLORS[index % COLORS.length]}
                />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        )}
      </ResponsiveContainer>
    </div>
  );
}

// Action Buttons Message Component
function ActionButtonsMessage({
  buttons,
  onAction,
}: {
  buttons: ActionButton[];
  onAction?: (action: string) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      {buttons.map((button, index) => (
        <motion.button
          key={index}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => onAction?.(button.action)}
          className={`px-4 py-2 rounded-lg font-medium transition-all ${
            button.variant === "primary"
              ? "bg-primary-600 hover:bg-primary-700 text-white shadow-md"
              : button.variant === "danger"
              ? "bg-red-600 hover:bg-red-700 text-white shadow-md"
              : "bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-900 dark:text-white"
          }`}
        >
          {button.label}
        </motion.button>
      ))}
    </div>
  );
}

// Progress Message Component
function ProgressMessage({ data }: { data: ProgressData }) {
  const percentage = (data.value / data.max) * 100;

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
          {data.label}
        </span>
        <span className="text-sm text-gray-600 dark:text-gray-400">
          {data.value} / {data.max}
        </span>
      </div>
      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 1, ease: "easeOut" }}
          className="h-full rounded-full"
          style={{
            backgroundColor: data.color || "#6366f1",
          }}
        />
      </div>
      <p className="text-xs text-gray-500 dark:text-gray-400 text-right">
        {percentage.toFixed(1)}% ukończono
      </p>
    </div>
  );
}

// Table Message Component
function TableMessage({ data }: { data: TableData }) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead className="bg-gray-50 dark:bg-gray-800">
          <tr>
            {data.headers.map((header, index) => (
              <th
                key={index}
                className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider"
              >
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
          {data.rows.map((row, rowIndex) => (
            <tr
              key={rowIndex}
              className="hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            >
              {row.map((cell, cellIndex) => (
                <td
                  key={cellIndex}
                  className="px-4 py-3 text-sm text-gray-700 dark:text-gray-300"
                >
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// Alert Message Component
function AlertMessage({ content }: { content: string }) {
  return (
    <div className="bg-yellow-50 dark:bg-yellow-900/20 border-l-4 border-yellow-400 p-4 rounded-r-lg">
      <div className="flex items-start gap-3">
        <svg
          className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path
            fillRule="evenodd"
            d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
            clipRule="evenodd"
          />
        </svg>
        <p className="text-yellow-800 dark:text-yellow-200 text-sm">
          {content}
        </p>
      </div>
    </div>
  );
}

// Example usage helper
export function createRichMessage(
  type: RichMessageType,
  data: any
): RichMessageData {
  return {
    type,
    content: typeof data === "string" ? data : undefined,
    data: typeof data !== "string" ? data : undefined,
  };
}
