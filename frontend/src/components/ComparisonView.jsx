import React, { useState } from "react";
import { Copy, Check, Download, Sparkles, FileText, ToggleLeft, ToggleRight } from "lucide-react";
import { diffWords } from "../utils/diff";

export default function ComparisonView({ originalText, enhancedText }) {
  const [showHighlights, setShowHighlights] = useState(true);
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (!enhancedText) return;
    try {
      await navigator.clipboard.writeText(enhancedText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy text", err);
    }
  };

  const handleDownloadTxt = () => {
    if (!enhancedText) return;
    const blob = new Blob([enhancedText], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "enhanced_academic_text.txt";
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleDownloadDocx = () => {
    if (!enhancedText) return;
    
    // Create MS Word HTML format which Word opens natively and lets the user save as a proper DOCX
    const formattedHtml = `
      <html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
      <head>
        <title>ScholarStyle Academic Text</title>
        <!--[if gte mso 9]>
        <xml>
          <w:WordDocument>
            <w:View>Normal</w:View>
            <w:Zoom>100</w:Zoom>
          </w:WordDocument>
        </xml>
        <![endif]-->
        <style>
          body {
            font-family: 'Calibri', 'Arial', sans-serif;
            font-size: 11pt;
            line-height: 1.5;
            color: #111827;
            padding: 1.5in;
          }
          p {
            margin-bottom: 12pt;
          }
          h1 {
            font-size: 18pt;
            color: #1e3a8a;
            margin-bottom: 16pt;
          }
        </style>
      </head>
      <body>
        <h1>Academic Text Rewriter Output</h1>
        ${enhancedText.split('\n').map(para => para.trim() ? `<p>${para}</p>` : '').join('')}
      </body>
      </html>
    `;
    
    const blob = new Blob(['\ufeff' + formattedHtml], { type: "application/msword;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "enhanced_academic_text.docx";
    link.click();
    URL.revokeObjectURL(url);
  };

  const renderDiff = () => {
    if (!originalText || !enhancedText) return <p className="whitespace-pre-wrap">{enhancedText}</p>;
    const diff = diffWords(originalText, enhancedText);

    return (
      <div className="whitespace-pre-wrap leading-relaxed">
        {diff.map((token, idx) => {
          if (token.type === "added") {
            return (
              <span
                key={idx}
                className="bg-emerald-100 dark:bg-emerald-950/40 text-emerald-900 dark:text-emerald-300 px-1 py-0.5 rounded font-medium border-b border-emerald-400/40 dark:border-emerald-600/30 mx-0.5"
              >
                {token.value}
              </span>
            );
          }
          if (token.type === "removed") {
            return (
              <span
                key={idx}
                className="bg-rose-100 dark:bg-rose-950/40 text-rose-900 dark:text-rose-300 px-1 py-0.5 rounded line-through opacity-60 border-b border-rose-400/40 dark:border-rose-600/30 mx-0.5"
              >
                {token.value}
              </span>
            );
          }
          return <span key={idx}>{token.value}</span>;
        })}
      </div>
    );
  };

  return (
    <div className="bg-neutral-50 dark:bg-neutral-950 border border-neutral-200 dark:border-neutral-800 rounded-3xl overflow-hidden shadow-inner flex flex-col h-[580px] transition-colors duration-300">
      
      {/* View Toolbar */}
      <div className="bg-white dark:bg-neutral-900 border-b border-neutral-200 dark:border-neutral-800 px-6 py-3.5 flex flex-wrap items-center justify-between gap-4 select-none transition-colors duration-300">
        <div className="flex items-center space-x-2">
          <Sparkles className="w-5 h-5 text-violet-600 dark:text-violet-400" />
          <span className="text-sm font-bold text-neutral-800 dark:text-neutral-200">
            Comparison Workbench
          </span>
        </div>

        <div className="flex items-center space-x-3">
          {/* Highlight Toggle */}
          <button
            onClick={() => setShowHighlights(!showHighlights)}
            className="flex items-center space-x-2 text-xs font-semibold text-neutral-600 dark:text-neutral-300 hover:text-violet-600 dark:hover:text-violet-400 bg-neutral-50 dark:bg-neutral-800 px-3 py-1.5 rounded-full border border-neutral-200/50 dark:border-neutral-700/50 transition-colors duration-200"
          >
            {showHighlights ? (
              <>
                <span>Edits Highlighted</span>
                <ToggleRight className="w-5 h-5 text-violet-600 dark:text-violet-400" />
              </>
            ) : (
              <>
                <span>Clean View</span>
                <ToggleLeft className="w-5 h-5 text-neutral-400" />
              </>
            )}
          </button>

          {/* Action Buttons */}
          <div className="flex items-center border-l border-neutral-200 dark:border-neutral-800 pl-3 space-x-2">
            <button
              onClick={handleCopy}
              disabled={!enhancedText}
              className={`p-2 rounded-lg transition-all duration-200 border ${
                copied
                  ? "bg-emerald-50 border-emerald-200 text-emerald-600 dark:bg-emerald-950/20 dark:border-emerald-900/50 dark:text-emerald-400"
                  : "bg-white hover:bg-neutral-50 dark:bg-neutral-850 dark:hover:bg-neutral-800 border-neutral-200/80 dark:border-neutral-700/80 text-neutral-600 dark:text-neutral-300 hover:text-neutral-900 dark:hover:text-white"
              } disabled:opacity-40 disabled:cursor-not-allowed`}
              title="Copy enhanced text"
            >
              {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
            </button>

            <button
              onClick={handleDownloadTxt}
              disabled={!enhancedText}
              className="p-2 rounded-lg bg-white hover:bg-neutral-50 dark:bg-neutral-850 dark:hover:bg-neutral-800 border border-neutral-200/80 dark:border-neutral-700/80 text-neutral-600 dark:text-neutral-300 hover:text-neutral-900 dark:hover:text-white transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed"
              title="Download as TXT"
            >
              <FileText className="w-4 h-4" />
            </button>

            <button
              onClick={handleDownloadDocx}
              disabled={!enhancedText}
              className="p-2 rounded-lg bg-white hover:bg-neutral-50 dark:bg-neutral-850 dark:hover:bg-neutral-800 border border-neutral-200/80 dark:border-neutral-700/80 text-neutral-600 dark:text-neutral-300 hover:text-neutral-900 dark:hover:text-white transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed"
              title="Download as Word DOCX"
            >
              <Download className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Editor Screens */}
      <div className="flex-1 grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-neutral-200 dark:divide-neutral-800 overflow-hidden">
        
        {/* Left Side: Original */}
        <div className="flex flex-col h-1/2 md:h-full overflow-hidden bg-white dark:bg-neutral-900 transition-colors duration-300">
          <div className="px-5 py-2 border-b border-neutral-100 dark:border-neutral-800/40 bg-neutral-50/50 dark:bg-neutral-900/50 flex justify-between items-center select-none">
            <span className="text-[10px] uppercase font-bold text-neutral-400 tracking-wider">
              Original Submission
            </span>
            <span className="text-[10px] text-neutral-400 font-medium">
              {originalText ? originalText.split(/\s+/).filter(Boolean).length : 0} words
            </span>
          </div>
          <div className="flex-1 p-6 overflow-y-auto text-sm text-neutral-600 dark:text-neutral-400 font-sans leading-relaxed select-text">
            {originalText ? (
              <p className="whitespace-pre-wrap">{originalText}</p>
            ) : (
              <div className="h-full flex items-center justify-center text-neutral-300 dark:text-neutral-700 italic select-none">
                Waiting for input text...
              </div>
            )}
          </div>
        </div>

        {/* Right Side: Enhanced / Diff */}
        <div className="flex flex-col h-1/2 md:h-full overflow-hidden bg-white dark:bg-neutral-900/90 transition-colors duration-300">
          <div className="px-5 py-2 border-b border-neutral-100 dark:border-neutral-800/40 bg-neutral-50/50 dark:bg-neutral-900/50 flex justify-between items-center select-none">
            <span className="text-[10px] uppercase font-bold text-violet-600 dark:text-violet-400 tracking-wider flex items-center">
              <span className="w-1.5 h-1.5 rounded-full bg-violet-600 mr-1.5"></span>
              Enhanced Style Result
            </span>
            <span className="text-[10px] text-neutral-400 font-medium">
              {enhancedText ? enhancedText.split(/\s+/).filter(Boolean).length : 0} words
            </span>
          </div>
          <div className="flex-1 p-6 overflow-y-auto text-sm text-neutral-900 dark:text-neutral-100 font-sans leading-relaxed select-text">
            {enhancedText ? (
              showHighlights ? renderDiff() : <p className="whitespace-pre-wrap">{enhancedText}</p>
            ) : (
              <div className="h-full flex items-center justify-center text-neutral-300 dark:text-neutral-700 italic select-none">
                Original text will be processed and compared here
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
