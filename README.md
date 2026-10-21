# ScholarStyle: AI Academic Text Rewriter & Style Enhancer

**ScholarStyle** is a production-ready, premium SaaS-style web application designed to rewrite AI-generated, informal, or rough drafts into polished, formal, and scholarly academic writing.

It offers an intuitive split-screen workbench, real-time readability indices, lexical diversity measurements, and word-level highlighted differences.

---

## 🚀 Quick Start (Windows)

To start the application, simply double-click the launcher script at the root of the project:

```bash
start_project.bat
```

This will automatically:
1. Verify Python and Node.js environments.
2. Install Python requirements.
3. Spin up the FastAPI backend (`http://127.0.0.1:8000`).
4. Spin up the Vite React frontend (`http://localhost:5173`).
5. Open your default web browser to the workbench.

---

## ⚙️ Manual Setup

If you prefer to start the servers manually, follow these instructions:

### 1. Backend (FastAPI)
1. Navigate to the `backend/` directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment (recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and configure your settings:
   ```bash
   copy .env.example .env
   ```
5. Run the server:
   ```bash
   python run.py
   ```
   The backend API will run on `http://127.0.0.1:8000`.

### 2. Frontend (React + Vite)
1. Navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```
2. Install Node packages (scaffolded dependencies + Tailwind v4 + Lucide):
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
   The web portal will open on `http://localhost:5173`.

---

## 🎯 Core Features

### 1. Split-Screen Comparison Workbench
- Side-by-side comparison of **Original Submission** vs. **Enhanced Style Result**.
- **Edits Highlighted View**: Computes dynamic word-level differences using a Longest Common Subsequence (LCS) diffing algorithm. Added words are highlighted in **green**, and deleted words in **red (with strikethrough)**.
- **Clean View Toggle**: Easily check the raw, uncluttered rewritten output.

### 2. Metrics & Analytics Dashboard
- **Readability Grade Level**: Evaluates linguistic difficulty before and after rewriting using the Flesch Reading Ease algorithm (re-tuned to recognize scientific hiatuses).
- **Lexical Richness (TTR)**: Measures Type-Token Ratio to check vocabulary density.
- **Style Coherence Index**: Gauges structural flow.
- **Applied Enhancements Log**: Bulleted log tracking modifications, structural adjustments, and vocabulary improvements.

### 3. Multiple Rewriting Settings
- **Academic Mode**: Objective phrasing, formal sentence starters, passive/active flow balance, contraction expansions, and academic terminology boosters.
- **Formal/Professional Mode**: Business-direct language, passive deletion, and grammatical correction.
- **Plain English/Clarity Mode**: Simplifies jargon for broader reading accessibility.

### 4. Direct Downloads
- Instantly export your rewritten academic text as a plain text file (`.txt`) or a Microsoft Word Document (`.docx`) with embedded styling headers.

---

## 🧠 NLP Pipeline & LLM Integrations

The backend implements a **hybrid cascading execution model** to guarantee high-performance, robust, and zero-downtime execution:

1. **Google Gemini API** *(Highest Quality)*: Uses `gemini-1.5-flash` if `GEMINI_API_KEY` is present in `backend/.env`.
2. **OpenAI API**: Uses `gpt-4o-mini` if `OPENAI_API_KEY` is present in `backend/.env`.
3. **Local Hugging Face Pipeline** *(Offline)*: If API keys are absent, it loads a local Transformer model (e.g. `google-t5/t5-small`) via PyTorch.
4. **Heuristics Rule Engine** *(Fallback)*: If running offline on a low-spec system without PyTorch, it falls back to a modular, rule-based substitution parsing tree to elevate vocabulary and adjust sentence structures.

---

## 📂 Project Structure

```
AI-Humanizer/
├── backend/
│   ├── app/
│   │   ├── __init__.py        # App packaging
│   │   ├── config.py          # Env & api key loading
│   │   ├── main.py            # API routing & endpoints
│   │   ├── nlp_pipeline.py    # Gemini/OpenAI/HF/Heuristic engines
│   │   └── utils.py           # Flesch index & sentence tokenizers
│   ├── .env.example
│   ├── requirements.txt
│   ├── test_app.py            # NLP logic unit tests
│   └── run.py                 # FastAPI runner
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ComparisonView.jsx  # Side-by-side highlight comparer
│   │   │   ├── Header.jsx          # Top logo & theme toggler
│   │   │   ├── MetricCard.jsx      # Animated stat delta cards
│   │   │   └── TextInput.jsx       # Custom text inputs (integrated in App)
│   │   ├── utils/
│   │   │   └── diff.js             # Word diff engine (LCS)
│   │   ├── App.jsx                 # Dashboard state manager
│   │   ├── index.css               # Tailwind v4 import & custom styles
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js              # Vite config with Tailwind v4 plugin
├── start_project.bat          # Easy double-click launch script
└── README.md
```
