from pydantic import BaseModel, Field

class RewriteRequest(BaseModel):
    text: str = Field(..., description="The raw input text to rewrite")
    mode: str = Field("academic", description="Target style mode: academic | formal | simple")

class RewriteResponse(BaseModel):
    original_text: str
    enhanced_text: str
    readability_before: float
    readability_after: float
    lexical_diversity_before: float
    lexical_diversity_after: float
    changes_summary: list[str]
    active_engine: str
