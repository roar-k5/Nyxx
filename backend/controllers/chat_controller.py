import asyncio
import os
from typing import Any, Dict, List, Optional

from fastapi import Request
from groq import AsyncGroq
from pydantic import BaseModel, Field

from backend.config import env as _env
from backend.models.analysis import AnalysisResult
from backend.models.message import save_message
from backend.services.analyzer import analyze_message
from backend.services.post_processor import PostProcessor
from backend.services.risk_engine import RiskEngine
from backend.safety.prompt_injection_filter import sanitize_for_llm


class HistoryMessage(BaseModel):
    role: str = Field(default="user")
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    history: List[HistoryMessage] = Field(default_factory=list)


def _load_helplines() -> List[Dict[str, Any]]:
    """Load helplines from environment or use defaults.
    
    Users can configure their own helplines via:
    - HELPLINES_JSON: Full JSON array of helpline objects
    - HELPLINE_1_NAME + HELPLINE_1_NUMBER: Individual helplines (up to 5)
    """
    import json
    env_helplines = os.getenv("HELPLINES_JSON")
    if env_helplines:
        try:
            return json.loads(env_helplines)
        except json.JSONDecodeError:
            pass
    
    # Check for individually configured helplines
    custom_helplines = []
    for i in range(1, 6):
        name = os.getenv(f"HELPLINE_{i}_NAME")
        number = os.getenv(f"HELPLINE_{i}_NUMBER")
        if name and number:
            custom_helplines.append({
                "name": name,
                "number": number,
                "available": os.getenv(f"HELPLINE_{i}_AVAILABLE", "24/7"),
                "note": os.getenv(f"HELPLINE_{i}_NOTE", ""),
            })
    
    if custom_helplines:
        return custom_helplines
    
    # Demo fallback helplines - clearly marked as demo/not real
    return [
        {
            "name": "Demo Helpline 1 (NOT REAL)",
            "number": "0000-DEMO-0000",
            "available": "Demo only",
            "note": "This is a demo app. Add your own helplines via HELPLINES_JSON or HELPLINE_1_NAME/NUMBER env vars.",
        },
        {
            "name": "Demo Emergency (NOT REAL)",
            "number": "0000-DEMO-911",
            "available": "Demo only",
            "note": "Configure real emergency numbers before using in production.",
        },
    ]


DEMO_HELPLINES: List[Dict[str, Any]] = _load_helplines()


def _client() -> Optional[AsyncGroq]:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    return AsyncGroq(api_key=api_key)


async def _generate_response(messages: List[Dict[str, str]]) -> str:
    client = _client()
    if client is None:
        return "NYXX is not configured yet. Add GROQ_API_KEY to the backend environment, then try again."

    try:
        completion = await client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            temperature=0.7,
            max_tokens=500,
            messages=messages,
        )
    except Exception as exc:
        print(f"Groq response generation failed: {exc}")
        return "I am having trouble connecting right now, but I am still here. Try again in a moment."

    return completion.choices[0].message.content or ""


def _normalize_analysis(message: str, analysis: Dict[str, Any]) -> AnalysisResult:
    emotion = str(analysis.get("emotion", "neutral")).lower()
    intent = str(analysis.get("intent", "conversation")).lower()
    risk_signals = analysis.get("riskSignals")
    if not isinstance(risk_signals, list):
        risk_signals = []

    lowered_message = message.lower()
    crisis_keywords = (
        "kill myself",
        "want to die",
        "end it all",
        "suicide",
        "self harm",
        "hurt myself",
        "can't go on",
    )
    high_risk_keywords = (
        "hopeless",
        "worthless",
        "panic attack",
        "don't want to be here",
        "overdose",
    )

    if any(keyword in lowered_message for keyword in crisis_keywords):
        crisis_level = "crisis"
        risk_score = 10
    elif any(keyword in lowered_message for keyword in high_risk_keywords) or risk_signals:
        crisis_level = "high"
        risk_score = 8
    elif emotion in {"distressed", "sad", "anxious", "lonely"}:
        crisis_level = "medium"
        risk_score = 5
    else:
        crisis_level = "low"
        risk_score = 2

    primary_emotion_map = {
        "happy": "hopeful",
        "confused": "overwhelmed",
        "distressed": "hopeless",
        "lonely": "sad",
    }
    primary_emotion = primary_emotion_map.get(emotion, emotion)
    allowed_emotions = {
        "anxious",
        "sad",
        "angry",
        "hopeless",
        "overwhelmed",
        "neutral",
        "hopeful",
        "grateful",
    }

    summary = str(analysis.get("summary", "")).strip()
    concerns = [str(signal) for signal in risk_signals if str(signal).strip()]
    if summary:
        concerns.append(summary)

    allowed_intents = {"venting", "seeking_advice", "asking_question", "crisis_signal", "general_chat"}
    normalized_intent = "crisis_signal" if crisis_level == "crisis" else intent

    return AnalysisResult(
        primary_emotion=primary_emotion if primary_emotion in allowed_emotions else "neutral",
        sentiment_score=-0.7 if risk_score >= 8 else -0.4 if risk_score >= 5 else -0.1,
        intent=normalized_intent if normalized_intent in allowed_intents else "general_chat",
        crisis_level=crisis_level,
        risk_score=risk_score,
        key_concerns=concerns[:3] if concerns else ["general support"],
        suggested_strategy=(
            "Validate feelings, keep the response gentle, and encourage immediate human support."
            if risk_score >= 8
            else "Respond with warm empathy and one small grounding suggestion."
        ),
    )


def _build_prompt(message: str, history: List[Dict[str, str]], analysis: AnalysisResult) -> List[Dict[str, str]]:
    system_prompt = (
        "You are Nyx, a warm AI companion. "
        "Be empathetic, concise, and non-clinical. "
        "Do not diagnose or claim professional credentials. "
        f"User emotion: {analysis.primary_emotion}. "
        f"Intent: {analysis.intent}. "
        f"Risk level: {analysis.crisis_level} ({analysis.risk_score}/10). "
        "Keep the reply under 3 short paragraphs."
    )
    return [
        {"role": "system", "content": system_prompt},
        *history[-6:],
        {"role": "user", "content": message},
    ]


from backend.middleware.security_logging import security_logger


async def send_message(payload: ChatRequest, request: Request) -> Dict[str, Any]:
    try:
        # Sanitize user input
        try:
            message = sanitize_for_llm(payload.message.strip())
        except ValueError as e:
            security_logger.prompt_injection_attempt(
                getattr(request.state, 'user_id', 'anonymous'),
                'injection_pattern_detected',
                request.client.host if request.client else None
            )
            return {
                "response": str(e),
                "emotion": "neutral",
                "crisis": False,
                "analysis": {
                    "primary_emotion": "neutral",
                    "sentiment_score": 0.0,
                    "intent": "general_chat",
                    "crisis_level": "low",
                    "risk_score": 1,
                    "key_concerns": ["input_validation"],
                    "suggested_strategy": "Respond with gentle empathy",
                },
                "disclaimer": "I'm an AI companion, not a therapist.",
            }

        history = [item.model_dump() for item in payload.history]

        raw_analysis = await analyze_message(message)
        analysis = _normalize_analysis(message, raw_analysis)
        risk = RiskEngine().assess_risk(analysis)
        prompt = _build_prompt(message=message, history=history, analysis=analysis)
        raw_response = await _generate_response(prompt)

        processor = PostProcessor()
        response, _ = processor.process(raw_response, risk)

        result: Dict[str, Any] = {
            "response": response,
            "emotion": analysis.primary_emotion,
            "crisis": bool(risk.escalate),
            "analysis": analysis.model_dump(),
            "disclaimer": processor.disclaimer,
        }

        if risk.escalate:
            result.update(
                {
                    "message": "We're really concerned about you right now. You're not alone.",
                    "helplines": DEMO_HELPLINES,
                    "banner": "DEMO MODE - These are test numbers. Real version uses actual helplines.",
                    "stay_option": "I'm here while you call",
                }
            )
            security_logger.crisis_detected(
                getattr(request.state, 'user_id', 'anonymous'),
                analysis.risk_score,
                request.client.host if request.client else None
            )

        database = getattr(request.app.state, "database", None)
        await asyncio.gather(
            save_message(database, "user", message, analysis.primary_emotion, bool(risk.escalate)),
            save_message(database, "assistant", response, analysis.primary_emotion, bool(risk.escalate)),
            return_exceptions=True,
        )

        security_logger.chat_message(
            getattr(request.state, 'user_id', 'anonymous'),
            len(message),
            analysis.primary_emotion,
            bool(risk.escalate),
            request.client.host if request.client else None
        )

        return result
    except Exception as exc:
        # Log detailed error internally, return generic message to client
        import logging
        logging.getLogger("nyx.chat").error(f"Chat flow failed: {exc}", exc_info=True)
        return {
            "response": "Something went wrong while NYXX was responding. Please try again.",
            "emotion": "neutral",
            "crisis": False,
            "analysis": {
                "primary_emotion": "neutral",
                "sentiment_score": 0.0,
                "intent": "general_chat",
                "crisis_level": "low",
                "risk_score": 2,
                "key_concerns": ["general support"],
                "suggested_strategy": "Respond with gentle empathy",
            },
            "disclaimer": "I'm an AI companion, not a therapist.",
        }
