from typing import List, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field

class AnalysisResult(BaseModel):
    """Module 1: Analyzer output"""
    primary_emotion: str = Field(..., description="Detected emotion: anxious, sad, angry, hopeless, overwhelmed, neutral, hopeful, grateful")
    sentiment_score: float = Field(..., ge=-1.0, le=1.0, description="-1.0 (negative) to 1.0 (positive)")
    intent: str = Field(..., description="User intent: venting, seeking_advice, asking_question, crisis_signal, general_chat")
    crisis_level: Literal["none", "low", "medium", "high", "crisis"] = Field(..., description="Crisis severity level")
    risk_score: int = Field(..., ge=0, le=10, description="Risk score 0-10")
    key_concerns: List[str] = Field(default_factory=list, description="List of identified concerns")
    suggested_strategy: str = Field(..., description="Strategy for response generation")

class RiskAssessment(BaseModel):
    """Module 2: Risk Engine output"""
    risk_level: Literal["low", "medium", "high", "crisis"]
    final_score: int = Field(..., ge=0, le=10)
    escalate: bool = Field(..., description="Whether to trigger crisis mode")
    temporal_context: Optional[str] = Field(None, description="Context from previous interactions")

class ChatMessage(BaseModel):
    """Individual chat message"""
    role: Literal["user", "assistant"]
    content: str
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    """Request to /api/chat"""
    message: str
    user_id: Optional[str] = "anonymous"
    history: Optional[List[ChatMessage]] = Field(default_factory=list)

class ChatResponse(BaseModel):
    """Response from /api/chat"""
    response: str
    crisis: bool = False
    analysis: Optional[AnalysisResult] = None
    risk_assessment: Optional[RiskAssessment] = None
    helplines: Optional[List["CrisisInfo"]] = None
    disclaimer: str = "I'm an AI companion, not a therapist. For serious concerns, please reach out to a mental health professional."

class CrisisInfo(BaseModel):
    """Crisis helpline information"""
    name: str
    number: str
    real_number: str
    available: str
    languages: Optional[str] = None
    whatsapp: Optional[bool] = False

class CrisisResponse(BaseModel):
    """Crisis mode response"""
    crisis: bool = True
    message: str
    helplines: List[CrisisInfo]
    banner: str = "⚠️ DEMO MODE — These are test numbers. Real version uses actual helplines."
