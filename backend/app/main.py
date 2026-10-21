from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from app.nlp_pipeline import NLPEngine
from app.utils import calculate_readability_score, calculate_lexical_diversity, generate_changes_summary
from app.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for AI Academic Text Rewriter & Style Enhancer",
    version="1.0.0"
)

# Configure CORS so the React frontend can talk to the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to actual frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RewriteRequest(BaseModel):
    text: str = Field(..., description="The raw input text to rewrite")
    mode: str = Field("academic", description="Target style mode: academic | formal | simple")

class RewriteResponse(BaseModel):
    original_text: str
    enhanced_text: str
    readability_score: float  # Enhanced text readability score
    readability_before: float  # Original text readability score
    readability_after: float  # Enhanced text readability score
    lexical_diversity_before: float
    lexical_diversity_after: float
    changes_summary: list[str]
    active_engine: str

@app.get("/")
def read_root():
    return {
        "message": "Welcome to AI Academic Text Rewriter & Style Enhancer API",
        "status": "online",
        "supported_modes": ["academic", "formal", "simple"]
    }

@app.post("/rewrite", response_model=RewriteResponse)
def rewrite_text(request: RewriteRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")
        
    try:
        # Perform style-based rewriting
        enhanced, engine = NLPEngine.rewrite(request.text, mode=request.mode)
        
        # Calculate statistics
        read_before = calculate_readability_score(request.text)
        read_after = calculate_readability_score(enhanced)
        
        lex_before = calculate_lexical_diversity(request.text)
        lex_after = calculate_lexical_diversity(enhanced)
        
        changes = generate_changes_summary(request.text, enhanced)
        
        return RewriteResponse(
            original_text=request.text,
            enhanced_text=enhanced,
            readability_score=read_after,  # Matches user's exact required output field name
            readability_before=read_before,
            readability_after=read_after,
            lexical_diversity_before=lex_before,
            lexical_diversity_after=lex_after,
            changes_summary=changes,
            active_engine=engine
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Rewriting pipeline error: {str(e)}")
