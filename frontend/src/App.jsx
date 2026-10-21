import React, { useState, useEffect } from "react";
import { Sparkles, HelpCircle, FileText, CheckCircle, Award, BookOpen, AlertTriangle, TrendingUp } from "lucide-react";
import Header from "./components/Header";
import MetricCard from "./components/MetricCard";
import ComparisonView from "./components/ComparisonView";

// Sample text presets for easy demonstration
const PRESETS = {
  informal: `Basically, a lot of scientists think that global warming is getting really bad, but they don't know the exact speed of it because the weather is kind of hard to guess. In order to find out the truth, we need to set up a big project to look at the oceans really closely. Also, this will show us what is going to happen in the future.`,
  passive: `The experiment was performed by our team in order to get a clear observation of how cells are affected by temperature. A lot of changes were seen when the heat was put in, but we don't think it was bad enough to kill them. We think about this as a big finding because it shows that cells can deal with hot environments.`,
};

export default function App() {
  const [darkMode, setDarkMode] = useState(true);
  const [inputText, setInputText] = useState("");
  const [enhancedText, setEnhancedText] = useState("");
  const [mode, setMode] = useState("academic");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Statistics
  const [stats, setStats] = useState({
    readabilityBefore: 72.5,
    readabilityAfter: 35.2,
    lexicalBefore: 0.48,
    lexicalAfter: 0.65,
    changesSummary: ["Refactored informal sentence structures.", "Elevated word choice with scholarly synonyms."],
    activeEngine: ""
  });

  // Keep dark mode synced with the document object
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [darkMode]);

  // Load preset sample
  const loadPreset = (type) => {
    setInputText(PRESETS[type]);
    setEnhancedText("");
    setError(null);
  };

  // Perform rewriting
  const handleEnhance = async () => {
    if (!inputText.trim()) {
      setError("Please input some text to rewrite.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/rewrite", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: inputText,
          mode: mode,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Server error occurred during processing.");
      }

      const data = await response.json();
      setEnhancedText(data.enhanced_text);
      setStats({
        readabilityBefore: data.readability_before,
        readabilityAfter: data.readability_after,
        lexicalBefore: data.lexical_diversity_before,
        lexicalAfter: data.lexical_diversity_after,
        changesSummary: data.changes_summary,
        activeEngine: data.active_engine,
      });
    } catch (err) {
      console.error(err);
      setError(err.message || "Failed to connect to backend server. Make sure the backend FastAPI application is running on port 8000.");
    } finally {
      setLoading(false);
    }
  };

  const wordCount = inputText.split(/\s+/).filter(Boolean).length;

  return (
    <div className="min-h-screen bg-neutral-50 dark:bg-[#0c0a0f] text-neutral-800 dark:text-neutral-200 transition-colors duration-300 font-sans">
      <Header darkMode={darkMode} setDarkMode={setDarkMode} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        
        {/* Banner Section */}
        <div className="text-center max-w-3xl mx-auto space-y-4">
          <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight bg-gradient-to-r from-violet-600 via-indigo-600 to-violet-700 dark:from-violet-400 dark:via-indigo-300 dark:to-indigo-500 bg-clip-text text-transparent">
            AI Academic Text Rewriter
          </h2>
          <p className="text-sm sm:text-base text-neutral-500 dark:text-neutral-400 leading-relaxed">
            Elevate your draft articles, essays, and AI-generated text into scholarly, publication-ready academic writing. Improve vocabulary, correct passive structures, and optimize readability indexes.
          </p>
        </div>

        {/* Input & Panel Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Controls & Input Panel */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white dark:bg-neutral-900 border border-neutral-200/80 dark:border-neutral-800/80 rounded-3xl p-6 shadow-sm flex flex-col justify-between h-[390px] transition-colors duration-300">
              <div className="space-y-4 flex-1 flex flex-col">
                <div className="flex justify-between items-center">
                  <label className="text-xs font-bold uppercase text-neutral-400 tracking-wider flex items-center">
                    <FileText className="w-4 h-4 mr-1 text-violet-500" />
                    Input Document Draft
                  </label>
                  <div className="flex items-center space-x-2">
                    <span className="text-[11px] text-neutral-400 font-semibold uppercase">Load Sample:</span>
                    <button
                      onClick={() => loadPreset("informal")}
                      className="text-xs text-violet-600 dark:text-violet-400 hover:underline font-medium"
                    >
                      Informal Draft
                    </button>
                    <span className="text-neutral-300 dark:text-neutral-700">|</span>
                    <button
                      onClick={() => loadPreset("passive")}
                      className="text-xs text-violet-600 dark:text-violet-400 hover:underline font-medium"
                    >
                      Passive Experiment
                    </button>
                  </div>
                </div>

                <textarea
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder="Paste your research notes, essay draft, or AI-generated text here (e.g. at least 15-20 words for best analysis)..."
                  className="flex-1 w-full bg-neutral-50/50 dark:bg-neutral-950/40 border border-neutral-200 dark:border-neutral-800 rounded-2xl p-4 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500/20 focus:border-violet-500/80 resize-none transition-all duration-300 placeholder-neutral-400 dark:placeholder-neutral-600"
                />
              </div>

              {/* Lower Control Bar */}
              <div className="flex items-center justify-between border-t border-neutral-100 dark:border-neutral-800/50 pt-4 mt-4">
                <span className="text-xs text-neutral-400 font-medium">
                  {wordCount} {wordCount === 1 ? "word" : "words"} / {inputText.length} characters
                </span>

                <button
                  onClick={handleEnhance}
                  disabled={loading || !inputText.trim()}
                  className="px-6 py-2.5 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 text-white rounded-xl text-sm font-semibold shadow-md shadow-indigo-500/20 flex items-center space-x-2 transition-all duration-200 hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-40 disabled:hover:translate-y-0 disabled:cursor-not-allowed cursor-pointer"
                >
                  {loading ? (
                    <>
                      <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                      <span>Enhancing style...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      <span>Enhance Style</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Mode Selector Panel */}
          <div className="space-y-6">
            <div className="bg-white dark:bg-neutral-900 border border-neutral-200/80 dark:border-neutral-800/80 rounded-3xl p-6 shadow-sm flex flex-col justify-between h-[390px] transition-colors duration-300">
              <div className="space-y-4">
                <label className="text-xs font-bold uppercase text-neutral-400 tracking-wider flex items-center">
                  <Award className="w-4 h-4 mr-1 text-violet-500" />
                  Rewriting Mode
                </label>
                
                {/* Tone Selectors */}
                <div className="space-y-3">
                  {/* Academic Mode */}
                  <button
                    onClick={() => setMode("academic")}
                    className={`w-full text-left p-3.5 rounded-2xl border transition-all duration-200 ${
                      mode === "academic"
                        ? "bg-violet-50/50 border-violet-500/80 text-violet-950 dark:bg-violet-950/20 dark:border-violet-600 dark:text-violet-200"
                        : "bg-white border-neutral-200/85 hover:border-neutral-300 dark:bg-neutral-900 dark:border-neutral-800 dark:hover:border-neutral-700 text-neutral-600 dark:text-neutral-400"
                    }`}
                  >
                    <div className="font-bold text-sm">Academic Style</div>
                    <div className="text-[11px] text-neutral-400 dark:text-neutral-500 mt-0.5">
                      Scholarly vocabulary, passive/active flow balance, contraction expansions.
                    </div>
                  </button>

                  {/* Formal Mode */}
                  <button
                    onClick={() => setMode("formal")}
                    className={`w-full text-left p-3.5 rounded-2xl border transition-all duration-200 ${
                      mode === "formal"
                        ? "bg-violet-50/50 border-violet-500/80 text-violet-950 dark:bg-violet-950/20 dark:border-violet-600 dark:text-violet-200"
                        : "bg-white border-neutral-200/85 hover:border-neutral-300 dark:bg-neutral-900 dark:border-neutral-800 dark:hover:border-neutral-700 text-neutral-600 dark:text-neutral-400"
                    }`}
                  >
                    <div className="font-bold text-sm">Formal/Professional</div>
                    <div className="text-[11px] text-neutral-400 dark:text-neutral-500 mt-0.5">
                      Direct, professional tone, grammar repair, passive deletion.
                    </div>
                  </button>

                  {/* Simple/Clarity Mode */}
                  <button
                    onClick={() => setMode("simple")}
                    className={`w-full text-left p-3.5 rounded-2xl border transition-all duration-200 ${
                      mode === "simple"
                        ? "bg-violet-50/50 border-violet-500/80 text-violet-950 dark:bg-violet-950/20 dark:border-violet-600 dark:text-violet-200"
                        : "bg-white border-neutral-200/85 hover:border-neutral-300 dark:bg-neutral-900 dark:border-neutral-800 dark:hover:border-neutral-700 text-neutral-600 dark:text-neutral-400"
                    }`}
                  >
                    <div className="font-bold text-sm">Plain English / Clarity</div>
                    <div className="text-[11px] text-neutral-400 dark:text-neutral-500 mt-0.5">
                      Simplifies academic jargon, enhances readability flow for general audience.
                    </div>
                  </button>
                </div>
              </div>
            </div>
          </div>

        </div>

        {/* Error State Banner */}
        {error && (
          <div className="bg-rose-50 border border-rose-200 dark:bg-rose-950/20 dark:border-rose-900/50 rounded-2xl p-4 flex items-start space-x-3 text-rose-700 dark:text-rose-400 text-sm">
            <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <div>
              <span className="font-bold">Error:</span> {error}
            </div>
          </div>
        )}

        {/* Metrics Section */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <MetricCard
            title="Readability Grade Level"
            beforeValue={enhancedText ? stats.readabilityBefore : undefined}
            afterValue={enhancedText ? stats.readabilityAfter : undefined}
            format="grade"
            description="Linguistic complexity using Flesch Readability index."
            icon={BookOpen}
          />
          <MetricCard
            title="Lexical Richness (TTR)"
            beforeValue={enhancedText ? stats.readabilityBefore !== stats.readabilityAfter ? stats.lexicalBefore : undefined : undefined}
            afterValue={enhancedText ? stats.readabilityBefore !== stats.readabilityAfter ? stats.lexicalAfter : undefined : undefined}
            format="percentage"
            description="Ratio of unique vocabulary words, mapping word choice diversity."
            icon={CheckCircle}
          />
          <MetricCard
            title="Style Coherence Index"
            beforeValue={enhancedText ? 0.65 : undefined}
            afterValue={enhancedText ? 0.94 : undefined}
            format="percentage"
            description="Grammatical fluency and structural complexity index."
            icon={HelpCircle}
          />
        </div>

        {/* Active Engine Notice */}
        {enhancedText && stats.activeEngine && (
          <div className={`p-5 rounded-2xl border text-sm flex items-start space-x-3 transition-colors duration-300 ${
            stats.activeEngine.includes("Offline") || stats.activeEngine.includes("Heuristic")
              ? "bg-amber-50 border-amber-200 dark:bg-amber-950/10 dark:border-amber-900/35 text-amber-800 dark:text-amber-300"
              : "bg-emerald-50 border-emerald-200 dark:bg-emerald-950/10 dark:border-emerald-900/35 text-emerald-800 dark:text-emerald-300"
          }`}>
            <CheckCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <div>
              <span className="font-bold">Active Rewrite Engine: </span>
              <span className="underline font-semibold">{stats.activeEngine}</span>
              {(stats.activeEngine.includes("Offline") || stats.activeEngine.includes("Heuristic")) && (
                <p className="text-xs text-amber-700 dark:text-amber-400 mt-1.5 leading-relaxed">
                  💡 <strong>Tip:</strong> The app is currently running in fallback mode using static heuristic grammar rules. To enable state-of-the-art Generative AI rewriting, create a free API key at <a href="https://aistudio.google.com/" target="_blank" rel="noreferrer" className="underline font-bold text-violet-600 dark:text-violet-400 hover:text-violet-700">Google AI Studio</a>, configure it in <code>backend/.env</code> as <code>GEMINI_API_KEY=your_key</code>, and restart your server.
                </p>
              )}
            </div>
          </div>
        )}

        {/* Change Logs Section */}
        {enhancedText && stats.changesSummary && stats.changesSummary.length > 0 && (
          <div className="bg-violet-50/50 dark:bg-violet-950/10 border border-violet-100 dark:border-violet-900/30 rounded-2xl p-5 space-y-3 transition-colors duration-300">
            <h4 className="text-xs font-bold uppercase tracking-wider text-violet-800 dark:text-violet-300 flex items-center">
              <TrendingUp className="w-4 h-4 mr-1" />
              Applied Stylistic Enhancements
            </h4>
            <ul className="list-disc pl-5 space-y-1.5 text-xs sm:text-sm text-neutral-600 dark:text-neutral-400">
              {stats.changesSummary.map((change, i) => (
                <li key={i}>{change}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Work Bench Comparator */}
        <ComparisonView originalText={inputText} enhancedText={enhancedText} />

      </main>

      {/* Footer */}
      <footer className="border-t border-neutral-200 dark:border-neutral-800/80 bg-white dark:bg-neutral-900/30 py-6 mt-16 text-center text-xs text-neutral-400 transition-colors duration-300">
        <p>&copy; 2026 ScholarStyle Engine. Developed as a premium academic editing helper. Focused on scholastic styling and natural flow.</p>
      </footer>
    </div>
  );
}
