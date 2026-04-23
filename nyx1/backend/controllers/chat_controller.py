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


class HistoryMessage(BaseModel):
    role: str = Field(default="user")
    content: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    history: List[HistoryMessage] = Field(default_factory=list)


DEMO_HELPLINES: List[Dict[str, Any]] = [
    {
        "name": "Tele MANAS (Demo)",
        "number": "14416-DEMO",
        "real_number": "14416",
        "available": "24/7",
        "languages": "22 languages",
    },
    {
        "name": "KIRAN Helpline (Demo)",
        "number": "1-800-TEST-HELP",
        "real_number": "1800-599-0019",
        "available": "24/7",
    },
    {
        "name": "Vandrevala Foundation (Demo)",
        "number": "+91-99999-DEMO",
        "real_number": "9999666555",
        "available": "24/7",
        "whatsapp": True,
    },
    {
        "name": "Emergency Services (Demo)",
        "number": "911-DEMO",
        "real_number": "112",
        "available": "24/7",
        "note": "Police/Ambulance",
    },
]


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


async def send_message(payload: ChatRequest, request: Request) -> Dict[str, Any]:
    try:
        message = payload.message.strip()
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

        database = getattr(request.app.state, "database", None)
        await asyncio.gather(
            save_message(database, "user", message, analysis.primary_emotion, bool(risk.escalate)),
            save_message(database, "assistant", response, analysis.primary_emotion, bool(risk.escalate)),
            return_exceptions=True,
        )

        return result
    except Exception as exc:
        print(f"Chat flow failed: {exc}")
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
