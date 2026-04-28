from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from typing import List, Optional
from backend.services.llm_service_full import LLMService
from backend.safety.detector import SafetyDetector
from backend.safety.prompt_injection_filter import sanitize_for_llm
from backend.middleware.rate_limiter import chat_limiter
from backend.authentication.auth_routes import get_current_user

router = APIRouter()

class AnalyzeRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    history: Optional[List[dict]] = []
    user_id: Optional[str] = "anonymous"

@router.post("/analyze")
async def analyze_message_endpoint(payload: AnalyzeRequest, request: Request, user=Depends(get_current_user)):
    """Standalone analysis endpoint — returns emotion, risk, intent without generating response."""
    chat_limiter.raise_if_limited(request)
    try:
        # Sanitize input
        message = sanitize_for_llm(payload.message)
        
        llm = LLMService()
        
        # Run safety detection
        safety = SafetyDetector()
        signals = safety.detect(message)
        
        # Run analysis
        from backend.models.analysis import ChatMessage
        history = [ChatMessage(**msg) for msg in payload.history] if payload.history else None
        analysis = await llm.analyze(message, history=history)
        
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
    except ValueError as e:
        return {
            "primary_emotion": "neutral",
            "sentiment_score": 0.0,
            "intent": "general_chat",
            "crisis_level": "low",
            "risk_score": 1,
            "key_concerns": ["input_validation"],
            "suggested_strategy": "Respond with gentle empathy",
            "safety_signals": {"crisis": False, "self_harm": False, "interpersonal_violence": False, "bullying": False, "harassment": False},
            "error": str(e),
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
