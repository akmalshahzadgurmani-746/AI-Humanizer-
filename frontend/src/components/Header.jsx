import React from "react";
import { Sun, Moon, GraduationCap, RefreshCw } from "lucide-react";

export default function Header({ darkMode, setDarkMode }) {
  return (
    <header className="border-b border-neutral-200 dark:border-neutral-800 bg-white/70 dark:bg-neutral-900/70 backdrop-blur-md sticky top-0 z-40 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="bg-gradient-to-tr from-violet-600 to-indigo-600 text-white p-2.5 rounded-xl shadow-md shadow-indigo-500/20">
            <GraduationCap className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-lg sm:text-xl font-bold bg-gradient-to-r from-neutral-900 via-violet-950 to-indigo-900 dark:from-white dark:via-violet-200 dark:to-indigo-200 bg-clip-text text-transparent leading-none">
              ScholarStyle
            </h1>
            <span className="text-[10px] text-violet-600 dark:text-violet-400 font-semibold tracking-wider uppercase">
              Academic Writer & Enhancer
            </span>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <div className="hidden md:flex items-center bg-violet-50 dark:bg-violet-950/30 px-3 py-1 rounded-full border border-violet-100 dark:border-violet-900/50">
            <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full mr-2 animate-pulse"></span>
            <span className="text-xs font-medium text-violet-950 dark:text-violet-300">
              NLP Engine Active
            </span>
          </div>

          <button
            onClick={() => setDarkMode(!darkMode)}
            className="p-2.5 rounded-xl bg-neutral-100 hover:bg-neutral-200 dark:bg-neutral-800 dark:hover:bg-neutral-700 text-neutral-600 dark:text-neutral-300 transition-all duration-200 border border-neutral-200/50 dark:border-neutral-700/50"
            aria-label="Toggle Theme"
          >
            {darkMode ? <Sun className="h-5 w-5 text-amber-400" /> : <Moon className="h-5 w-5 text-indigo-950" />}
          </button>
        </div>
      </div>
    </header>
  );
}
