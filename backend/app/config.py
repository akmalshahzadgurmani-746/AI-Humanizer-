import os
from pathlib import Path
from dotenv import load_dotenv

# Load env variables from backend root directory or parent workspace
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

class Settings:
    PROJECT_NAME: str = "AI Academic Text Rewriter & Style Enhancer"
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Local Hugging Face Settings
    ENABLE_LOCAL_HF: bool = os.getenv("ENABLE_LOCAL_HF", "true").lower() in ("true", "1", "yes")
    HF_MODEL_NAME: str = os.getenv("HF_MODEL_NAME", "google-t5/t5-small")
    
    # Fallback to rule-based parser if everything else fails/is disabled
    ALLOW_HEURISTIC_FALLBACK: bool = True

settings = Settings()
