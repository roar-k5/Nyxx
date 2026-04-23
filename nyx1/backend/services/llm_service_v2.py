import asyncio
import json
import os
import random
import re
from typing import List, Optional

import httpx

from app.models.analysis import AnalysisResult, ChatMessage
from app.safety import SafetyDetector


class LLMService:
    """Module 1 (Analyzer) and Module 4 (Response Generator)."""

    def __init__(
        self,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """
        Args:
            provider: 'ollama', 'lmstudio', 'gemini', 'groq', or 'mock'
            api_key: API key for Gemini or Groq (optional)
            base_url: Custom base URL for local LLM
        """
        self.provider = provider or os.getenv("LLM_PROVIDER", "ollama")
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")

        if self.provider == "ollama":
            self.base_url = base_url or os.getenv("OLLAMA_URL", "http://localhost:11434")
            self.model = os.getenv("OLLAMA_MODEL", "mistral")
        elif self.provider == "lmstudio":
            self.base_url = base_url or os.getenv("LMSTUDIO_URL", "http://localhost:1234")
            self.model = os.getenv("LMSTUDIO_MODEL", "local-model")
        elif self.provider == "gemini":
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY required for Gemini provider")
            from google import genai

            self.client = genai.Client(api_key=self.api_key)
            self.model = "gemini-2.0-flash-lite"
        elif self.provider == "groq":
            if not self.groq_api_key:
                raise ValueError("GROQ_API_KEY required for Groq provider")
            self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
            self.base_url = "https://api.groq.com/openai/v1"
        elif self.provider == "mock":
            self.mock_mode = True
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

        self.mock_mode = self.provider == "mock"
        self.timeout = 60
        self.debug = os.getenv("NYX_DEBUG", "").strip().lower() in {"1", "true", "yes", "on"}
        self.safety = SafetyDetector()

    def _debug(self, message: str) -> None:
        if self.debug:
            print(f"DEBUG: {message}")

    def _message_suggests_interpersonal_violence(
        self,
        message: str,
        history: Optional[List[ChatMessage]] = None,
    ) -> bool:
        return self.safety.detects_interpersonal_violence(message, history)

    def _message_suggests_self_harm(
        self,
        message: str,
        history: Optional[List[ChatMessage]] = None,
    ) -> bool:
        return self.safety.detects_self_harm(message, history)

    def _message_is_context_continuation(
        self,
        message: str,
    ) -> bool:
        """Detect short continuation/interruption phrases."""
        msg = message.strip().lower()
        continuation_phrases = [
            "well",
            "well...",
            "hmm",
            "uh",
            "wait",
            "bro let me complete",
            "let me complete",
            "let me finish",
            "hear me out",
            "hold on",
            "one sec",
            "i'm typing",
            "im typing",
        ]
        if msg in continuation_phrases:
            return True
        if any(phrase in msg for phrase in continuation_phrases):
            return True
        return False

    def _apply_safety_overrides(
        self,
        message: str,
        analysis: AnalysisResult,
        history: Optional[List[ChatMessage]] = None,
    ) -> AnalysisResult:
        """Apply conservative heuristics on top of the model output."""
        signals = self.safety.detect(message, history)

        if signals.self_harm:
            concerns = list(
                dict.fromkeys(
                    [
                        *analysis.key_concerns,
                        "suicidal_ideation",
                        "self_harm",
                    ]
                )
            )
            return analysis.model_copy(
                update={
                    "primary_emotion": "hopeless",
                    "intent": "crisis_signal",
                    "crisis_level": "crisis",
                    "risk_score": 10,
                    "key_concerns": concerns,
                    "suggested_strategy": "Immediate crisis intervention required",
                }
            )

        if signals.harassment:
            concerns = list(dict.fromkeys([*analysis.key_concerns, "harassment", "unsafe_environment"]))
            return analysis.model_copy(
                update={
                    "primary_emotion": "anxious",
                    "intent": "seeking_advice" if analysis.intent == "general_chat" else analysis.intent,
                    "crisis_level": "medium" if analysis.crisis_level in {"none", "low"} else analysis.crisis_level,
                    "risk_score": max(analysis.risk_score, 6),
                    "key_concerns": concerns,
                    "suggested_strategy": "Prioritize personal safety, boundaries, and trusted support",
                }
            )

        if signals.bullying:
            concerns = list(dict.fromkeys([*analysis.key_concerns, "bullying", "social_distress"]))
            return analysis.model_copy(
                update={
                    "primary_emotion": "sad" if analysis.primary_emotion == "neutral" else analysis.primary_emotion,
                    "intent": "venting" if analysis.intent == "general_chat" else analysis.intent,
                    "crisis_level": "low" if analysis.crisis_level == "none" else analysis.crisis_level,
                    "risk_score": max(analysis.risk_score, 4),
                    "key_concerns": concerns,
                    "suggested_strategy": "Validate impact, suggest trusted adult/support and documentation if needed",
                }
            )

        if self._message_is_context_continuation(message):
            concerns = list(dict.fromkeys([*analysis.key_concerns, "user_continuing_thought"]))
            return analysis.model_copy(
                update={
                    "primary_emotion": "neutral",
                    "intent": "general_chat",
                    "crisis_level": "none",
                    "risk_score": 1,
                    "key_concerns": concerns,
                    "suggested_strategy": "Acknowledge and invite them to continue their thought",
                }
            )

        if not signals.interpersonal_violence:
            return analysis

        concerns = list(
            dict.fromkeys(
                [
                    *analysis.key_concerns,
                    "aggression",
                    "interpersonal_violence_risk",
                ]
            )
        )

        return analysis.model_copy(
            update={
                "primary_emotion": "angry",
                "intent": "venting" if analysis.intent == "general_chat" else analysis.intent,
                "crisis_level": (
                    "medium" if analysis.crisis_level in {"none", "low"} else analysis.crisis_level
                ),
                "risk_score": max(analysis.risk_score, 6),
                "key_concerns": concerns,
                "suggested_strategy": "De-escalate, refuse harm, encourage distance and calming steps",
            }
        )

    def _mock_analyze(self, message: str) -> AnalysisResult:
        """Smart keyword-based emotion detection for mock mode."""
        message_lower = message.lower()

        crisis_patterns = [
            "kill myself",
            "suicide",
            "end my life",
            "want to die",
            "hurt myself",
            "self-harm",
            "no point living",
            "better off dead",
            "can't go on",
            "end it all",
        ]
        for pattern in crisis_patterns:
            if pattern in message_lower:
                return AnalysisResult(
                    primary_emotion="hopeless",
                    sentiment_score=-0.9,
                    intent="crisis_signal",
                    crisis_level="crisis",
                    risk_score=10,
                    key_concerns=["suicidal_ideation", "self_harm"],
                    suggested_strategy="Immediate crisis intervention required",
                )

        high_distress = [
            "hopeless",
            "worthless",
            "giving up",
            "can't take it",
            "breaking down",
            "losing my mind",
            "numb",
            "empty inside",
        ]
        for pattern in high_distress:
            if pattern in message_lower:
                return AnalysisResult(
                    primary_emotion="hopeless",
                    sentiment_score=-0.7,
                    intent="venting",
                    crisis_level="high",
                    risk_score=8,
                    key_concerns=["depression", "hopelessness"],
                    suggested_strategy="Validate pain, encourage professional help",
                )

        anxiety_words = [
            "anxious",
            "worried",
            "panic",
            "stress",
            "nervous",
            "overwhelmed",
            "can't breathe",
            "racing thoughts",
            "restless",
            "on edge",
            "tense",
            "scared about",
        ]
        if any(word in message_lower for word in anxiety_words):
            return AnalysisResult(
                primary_emotion="anxious",
                sentiment_score=-0.4,
                intent="venting",
                crisis_level="low",
                risk_score=5,
                key_concerns=["anxiety", "stress"],
                suggested_strategy="Grounding techniques, reassurance",
            )

        sadness_words = [
            "sad",
            "cry",
            "crying",
            "tears",
            "lonely",
            "alone",
            "miss them",
            "grief",
            "heartbroken",
            "hurt",
            "pain",
            "disappointed",
            "let down",
            "not fair",
        ]
        if any(word in message_lower for word in sadness_words):
            return AnalysisResult(
                primary_emotion="sad",
                sentiment_score=-0.5,
                intent="venting",
                crisis_level="low",
                risk_score=4,
                key_concerns=["sadness", "loneliness"],
                suggested_strategy="Empathy, validation, gentle listening",
            )

        anger_words = [
            "angry",
            "mad",
            "furious",
            "hate",
            "annoyed",
            "frustrated",
            "pissed",
            "rage",
            "can't stand",
            "so done with",
            "fed up",
        ]
        if any(word in message_lower for word in anger_words):
            return AnalysisResult(
                primary_emotion="angry",
                sentiment_score=-0.4,
                intent="venting",
                crisis_level="low",
                risk_score=3,
                key_concerns=["anger", "frustration"],
                suggested_strategy="Acknowledge frustration, de-escalation",
            )

        overwhelm_words = [
            "too much",
            "overwhelmed",
            "burned out",
            "exhausted",
            "can't handle",
            "drowning",
            "suffocating",
            "pressure",
        ]
        if any(word in message_lower for word in overwhelm_words):
            return AnalysisResult(
                primary_emotion="overwhelmed",
                sentiment_score=-0.5,
                intent="venting",
                crisis_level="medium",
                risk_score=6,
                key_concerns=["burnout", "overwhelm"],
                suggested_strategy="Validate tiredness, suggest small steps",
            )

        positive_words = [
            "happy",
            "great",
            "amazing",
            "love",
            "excited",
            "grateful",
            "thankful",
            "blessed",
            "best day",
            "so good",
            "wonderful",
            "fantastic",
            "joy",
        ]
        if any(word in message_lower for word in positive_words):
            return AnalysisResult(
                primary_emotion="grateful",
                sentiment_score=0.7,
                intent="general_chat",
                crisis_level="none",
                risk_score=1,
                key_concerns=["positive_mood"],
                suggested_strategy="Celebrate with them",
            )

        greeting_words = [
            "hi",
            "hello",
            "hey",
            "hii",
            "hiii",
            "yo",
            "sup",
            "what's up",
            "good morning",
            "good evening",
        ]
        if any(word in message_lower for word in greeting_words) and len(message_lower.split()) <= 3:
            return AnalysisResult(
                primary_emotion="neutral",
                sentiment_score=0.0,
                intent="general_chat",
                crisis_level="none",
                risk_score=1,
                key_concerns=["greeting"],
                suggested_strategy="Warm casual greeting",
            )

        return AnalysisResult(
            primary_emotion="neutral",
            sentiment_score=0.0,
            intent="general_chat",
            crisis_level="none",
            risk_score=2,
            key_concerns=["general"],
            suggested_strategy="Casual conversation",
        )

    def _mock_generate_response(self, message: str, analysis: AnalysisResult) -> str:
        """Smart response generation for mock mode."""
        responses = {
            "anxious": [
                "That sounds heavy, fr. Let's do one slow breath together first. Want to tell me what's hitting hardest right now?",
                "I hear you, anxiety can be a lot 😮‍💨. Try unclenching your jaw and shoulders for 10 seconds. What's the biggest stressor at this moment?",
            ],
            "sad": [
                "I'm really sorry you're feeling this way. You're not alone in this, and I'm here with you. Want to tell me what happened?",
                "That sounds painful, ngl. If you can, text one trusted person right now and say you need support. What feels heaviest today?",
            ],
            "angry": [
                "I hear you, that sounds infuriating. Before anything else, take a quick step back and sip some water. What set this off?",
                "Yeah, that would make anyone mad. Let's keep you safe and calm first. What's one move you can make in 5 minutes to cool down?",
            ],
            "hopeless": [
                "I'm really glad you said this out loud. You deserve support right now, not later. Can you reach out to one trusted person or helpline now?",
                "This sounds really intense, and you shouldn't carry it alone. Please contact someone safe right now. Do you want to stay here while you do it?",
            ],
            "overwhelmed": [
                "That's a lot to carry. Pick just one tiny next step for the next 10 minutes. Which task feels easiest to start?",
                "Totally get it, this is overload mode. Pause, take 3 slow breaths, then choose one small thing only. Want help picking it?",
            ],
            "grateful": [
                "Love this energy ✨. What's been going right today?",
                "That's awesome, fr. Want to lock this win in with one small habit for tomorrow?",
            ],
            "neutral": [
                "Hey, what's up? How are you feeling today?",
                "Yo, I'm here for you. What's on your mind?",
            ],
        }
        return random.choice(responses.get(analysis.primary_emotion, responses["neutral"]))

    async def _call_ollama(self, prompt: str) -> str:
        """Call local Ollama API."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 500,
                    },
                },
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()

    async def _call_lmstudio(self, prompt: str) -> str:
        """Call LM Studio API."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 500,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()

    async def _call_gemini(self, prompt: str) -> str:
        """Call Gemini API."""
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        return response.text.strip()  # type: ignore

    async def _call_groq(self, prompt: str) -> str:
        """Call Groq API."""
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 500,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()

    async def _call_llm(self, prompt: str) -> str:
        """Route to the appropriate LLM backend."""
        if self.mock_mode:
            await asyncio.sleep(0.5)
            if "primary_emotion" in prompt:
                return (
                    '{"primary_emotion": "neutral", "sentiment_score": 0.0, '
                    '"intent": "general_chat", "crisis_level": "none", '
                    '"risk_score": 2, "key_concerns": ["general"], '
                    '"suggested_strategy": "casual conversation"}'
                )
            return "Hey! I'm here and ready to chat. What's on your mind?"

        if self.provider == "ollama":
            return await self._call_ollama(prompt)
        if self.provider == "lmstudio":
            return await self._call_lmstudio(prompt)
        if self.provider == "gemini":
            return await self._call_gemini(prompt)
        if self.provider == "groq":
            return await self._call_groq(prompt)
        raise ValueError(f"Unknown provider: {self.provider}")

    def _extract_json(self, text: str) -> dict:
        """Extract JSON from a response body."""
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        json_pattern = r'\{[\s\S]*?"primary_emotion"[\s\S]*?\}'
        match = re.search(json_pattern, text)
        if match:
            text = match.group(0)

        return json.loads(text)

    def _build_history_context(
        self,
        history: Optional[List[ChatMessage]],
        max_messages: int = 10,
        min_user_messages: int = 3,
    ) -> str:
        """Build compact context while preserving recent user intent."""
        if not history:
            return ""

        recent = history[-max_messages:]
        user_count = sum(1 for msg in recent if msg.role == "user")
        if user_count < min_user_messages:
            recent_users = [msg for msg in history if msg.role == "user"][-min_user_messages:]
            seen = {(msg.role, msg.content, msg.timestamp) for msg in recent}
            for user_msg in recent_users:
                marker = (user_msg.role, user_msg.content, user_msg.timestamp)
                if marker not in seen:
                    recent.insert(0, user_msg)
                    seen.add(marker)

        lines = [f"{msg.role}: {msg.content}" for msg in recent]
        return "\nRecent conversation:\n" + "\n".join(lines)

    async def analyze(
        self,
        message: str,
        history: Optional[List[ChatMessage]] = None,
    ) -> AnalysisResult:
        """Module 1: Analyze user message."""
        if self.mock_mode:
            self._debug("Using SMART MOCK analyzer")
            analysis = self._mock_analyze(message)
            return self._apply_safety_overrides(message, analysis, history)

        history_context = self._build_history_context(history, max_messages=10, min_user_messages=3)

        prompt = f"""Analyze this message and return ONLY a JSON object. No markdown, no explanation.

Message: "{message}"{history_context}

Return EXACTLY this format:
{{"primary_emotion": "anxious", "sentiment_score": -0.3, "intent": "venting", "crisis_level": "low", "risk_score": 3, "key_concerns": ["concern"], "suggested_strategy": "be supportive"}}

Allowed emotions: anxious, sad, angry, hopeless, overwhelmed, neutral, hopeful, grateful
Allowed intents: venting, seeking_advice, asking_question, crisis_signal, general_chat
Allowed crisis_levels: none, low, medium, high, crisis

Risk scoring (0-10):
- 9-10 = crisis (suicidal ideation)
- 7-8 = high (severe distress)
- 5-6 = medium (struggling)
- 0-4 = low/normal

Analyze now:"""

        try:
            text = await self._call_llm(prompt)
            self._debug(f"Raw analysis response: {text[:300]}...")

            data = self._extract_json(text)
            required = [
                "primary_emotion",
                "sentiment_score",
                "intent",
                "crisis_level",
                "risk_score",
                "key_concerns",
                "suggested_strategy",
            ]
            defaults = {
                "primary_emotion": "neutral",
                "sentiment_score": 0.0,
                "intent": "general_chat",
                "crisis_level": "none",
                "risk_score": 2,
                "key_concerns": [],
                "suggested_strategy": "Respond with gentle empathy",
            }
            for field in required:
                data.setdefault(field, defaults[field])

            analysis = AnalysisResult(**data)
            return self._apply_safety_overrides(message, analysis, history)

        except Exception as e:
            self._debug(f"Analysis parse error: {e}")
            fallback = AnalysisResult(
                primary_emotion="neutral",
                sentiment_score=0.0,
                intent="general_chat",
                crisis_level="none",
                risk_score=2,
                key_concerns=["general"],
                suggested_strategy="Respond with gentle empathy",
            )
            return self._apply_safety_overrides(message, fallback, history)

    async def generate_response(
        self,
        message: str,
        analysis: AnalysisResult,
        history: Optional[List[ChatMessage]] = None,
    ) -> str:
        """Module 4: Generate an empathetic response."""
        self._debug(f"Generating response with provider={self.provider}, mock_mode={self.mock_mode}")

        if self._message_suggests_interpersonal_violence(message, history):
            return (
                "I can't help with hurting someone. If you're this fired up, "
                "the safest move is to put some space between you and them for a bit, "
                "unclench your body, and let the heat come down. "
                "What's one thing you can do in the next 10 minutes to avoid acting on this?"
            )

        if self._message_is_context_continuation(message):
            return (
                "My bad, go ahead bro. "
                "I'm listening. "
                "Take your time and finish what you wanted to say."
            )

        if self.mock_mode or self.provider == "mock":
            self._debug("Using SMART MOCK response generator")
            return self._mock_generate_response(message, analysis)

        history_context = self._build_history_context(history, max_messages=10, min_user_messages=3)

        risk_note = ""
        if analysis.risk_score >= 7:
            risk_note = "\nImportant: The user is showing high distress. Gently encourage professional help."
        elif analysis.risk_score >= 5:
            risk_note = "\nNote: The user is struggling. Be extra supportive."

        prompt = f"""You are Nyx, a mental health companion who chats like a bubbly Indian Gen-Z friend.

User's emotional state:
- Emotion: {analysis.primary_emotion}
- Intent: {analysis.intent}
- Risk level: {analysis.crisis_level} (score: {analysis.risk_score}/10)
- Key concerns: {', '.join(analysis.key_concerns)}
- Strategy: {analysis.suggested_strategy}{risk_note}{history_context}

User's message: "{message}"

Respond as a caring friend would:
1. Validate their feelings first (1 sentence)
2. Offer gentle support or perspective (1 sentence)
3. End with either a soft open question OR one specific next step

Constraints:
- Keep it short: 1-3 lines max
- Casual, cheeky, warm - Indian Gen-Z energy
- Never diagnose or give medical advice
- Natural, conversational tone with simple words
- Light slang is okay when it matches the user vibe
- Use at most one supportive emoji
- If risk score >= 5, include one clear call-to-action
- Do not use "Hey there" or "I'm here for you" repeatedly
- Vary your responses, don't repeat the same lines

Your response:"""

        try:
            result = await self._call_llm(prompt)
            self._debug(f"Raw response from LLM: {result[:200]}...")
            return result
        except Exception as e:
            self._debug(f"Response generation error: {e}")
            return "I'm here with you. Tell me more about what's on your mind?"
