import React from "react";
import { ArrowUpRight, ArrowDownRight, TrendingUp } from "lucide-react";

export default function MetricCard({ title, beforeValue, afterValue, format = "decimal", description, icon: Icon }) {
  const getDelta = () => {
    if (beforeValue === undefined || afterValue === undefined) return null;
    const diff = afterValue - beforeValue;
    return diff;
  };

  const delta = getDelta();

  const formatValue = (val) => {
    if (val === undefined || val === null) return "-";
    if (format === "percentage") {
      return `${Math.round(val * 100)}%`;
    }
    if (format === "score") {
      return val.toFixed(1);
    }
    if (format === "grade") {
      if (val >= 90) return "5th Grade (Very Easy)";
      if (val >= 80) return "6th Grade (Easy)";
      if (val >= 70) return "7th Grade (Fairly Easy)";
      if (val >= 60) return "8th-9th Grade (Standard)";
      if (val >= 50) return "High School (Fairly Hard)";
      if (val >= 30) return "College Level (Difficult)";
      return "Graduate Level (Academic)";
    }
    return val;
  };

  const getDeltaDisplay = () => {
    if (delta === null || delta === 0) return null;
    const isIncrease = delta > 0;
    
    // For Readability: lower score means more advanced academic language
    // For Lexical diversity: higher score is better.
    let colorClass = "text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/20";
    let isPositiveChange = isIncrease;

    if (title.toLowerCase().includes("readability")) {
      // Lower readability index represents higher linguistic complexity, which is positive for scholarly text
      isPositiveChange = !isIncrease;
      colorClass = isPositiveChange 
        ? "text-violet-600 dark:text-violet-400 bg-violet-50 dark:bg-violet-950/20" 
        : "text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/20";
    }

    const absDelta = format === "percentage" ? `${Math.round(Math.abs(delta) * 100)}%` : Math.abs(delta).toFixed(1);

    return (
      <div className={`flex items-center px-2 py-0.5 rounded-full text-xs font-semibold ${colorClass}`}>
        {isIncrease ? <ArrowUpRight className="w-3.5 h-3.5 mr-0.5" /> : <ArrowDownRight className="w-3.5 h-3.5 mr-0.5" />}
        <span>{absDelta} {title.toLowerCase().includes("readability") ? (isIncrease ? "simpler" : "scholarly") : ""}</span>
      </div>
    );
  };

  return (
    <div className="bg-white dark:bg-neutral-900 border border-neutral-200/80 dark:border-neutral-800/80 rounded-2xl p-5 shadow-sm hover:shadow-md transition-all duration-300 flex flex-col justify-between group">
      <div>
        <div className="flex items-center justify-between mb-4">
          <span className="text-sm font-semibold text-neutral-500 dark:text-neutral-400 tracking-wide uppercase">
            {title}
          </span>
          <div className="p-2 bg-neutral-50 dark:bg-neutral-800/50 rounded-xl group-hover:bg-violet-50 dark:group-hover:bg-violet-950/30 transition-colors duration-300 text-neutral-400 dark:text-neutral-500 group-hover:text-violet-600 dark:group-hover:text-violet-400">
            <Icon className="w-5 h-5" />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 border-b border-neutral-100 dark:border-neutral-800/50 pb-4 mb-4">
          <div>
            <div className="text-[10px] uppercase font-semibold text-neutral-400 dark:text-neutral-500 mb-1">
              Before
            </div>
            <div className="text-lg font-bold text-neutral-700 dark:text-neutral-300 truncate">
              {formatValue(beforeValue)}
            </div>
          </div>
          <div className="border-l border-neutral-100 dark:border-neutral-800/50 pl-4">
            <div className="text-[10px] uppercase font-semibold text-neutral-400 dark:text-neutral-500 mb-1 flex items-center justify-between">
              After
            </div>
            <div className="text-xl font-black text-neutral-900 dark:text-white truncate">
              {formatValue(afterValue)}
            </div>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <span className="text-xs text-neutral-400 dark:text-neutral-500 max-w-[70%]">
          {description}
        </span>
        {getDeltaDisplay()}
      </div>
    </div>
  );
}
