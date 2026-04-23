from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from backend.services.llm_service_full import LLMService
from backend.safety.detector import SafetyDetector

router = APIRouter()

class AnalyzeRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = []
    user_id: Optional[str] = "anonymous"

@router.post("/analyze")
async def analyze_message_endpoint(payload: AnalyzeRequest):
    """Standalone analysis endpoint — returns emotion, risk, intent without generating response."""
    try:
        llm = LLMService()
        
        # Run safety detection
        safety = SafetyDetector()
        signals = safety.detect(payload.message)
        
        # Run analysis
        from backend.models.analysis import ChatMessage
        history = [ChatMessage(**msg) for msg in payload.history] if payload.history else None
        analysis = await llm.analyze(payload.message, history=history)
        
        return {
            "primary_emotion": analysis.primary_emotion,
            "sentiment_score": analysis.sentiment_score,
            "intent": analysis.intent,
            "crisis_level": analysis.crisis_level,
            "risk_score": analysis.risk_score,
            "key_concerns": analysis.key_concerns,
            "suggested_strategy": analysis.suggested_strategy,
            "safety_signals": {
                "crisis": signals.crisis,
                "self_harm": signals.self_harm,
                "interpersonal_violence": signals.interpersonal_violence,
                "bullying": signals.bullying,
                "harassment": signals.harassment,
            }
        }
    except Exception as exc:
        print(f"Analyze endpoint failed: {exc}")
        return {
            "primary_emotion": "neutral",
            "sentiment_score": 0.0,
            "intent": "general_chat",
            "crisis_level": "low",
            "risk_score": 3,
            "key_concerns": ["general"],
            "suggested_strategy": "Respond with gentle empathy",
            "safety_signals": {"crisis": False, "self_harm": False, "interpersonal_violence": False, "bullying": False, "harassment": False},
            "error": str(exc),
        }
