from typing import List, Optional
from backend.models.analysis import AnalysisResult, ChatMessage
from backend.config.prompts import (
    NYX_CORE_PROMPT,
    NYX_GREETING_PROMPT,
    NYX_CRISIS_PROMPT,
    NYX_OFFTOPIC_PROMPT,
    NYX_EMOTION_GUIDANCE,
    NYX_INTENT_PROMPTS,
    NYX_RISK_PROMPTS,
)

class PromptBuilder:
    """Module 3: Assemble context for response generation using Nyx personality prompts"""
    
    def __init__(self):
        self.core_prompt = NYX_CORE_PROMPT
    
    def _get_emotion_guidance(self, emotion: str) -> str:
        """Get guidance based on detected emotion"""
        return NYX_EMOTION_GUIDANCE.get(emotion.lower(), NYX_EMOTION_GUIDANCE["neutral"])
    
    def _get_intent_guidance(self, intent: str) -> str:
        """Get guidance based on user intent"""
        return NYX_INTENT_PROMPTS.get(intent.lower(), NYX_INTENT_PROMPTS["general_chat"])
    
    def _get_risk_guidance(self, risk_level: str) -> str:
        """Get guidance based on risk level"""
        return NYX_RISK_PROMPTS.get(risk_level.lower(), NYX_RISK_PROMPTS["low"])
    
    def build_response_prompt(
        self,
        message: str,
        analysis: AnalysisResult,
        history: Optional[List[ChatMessage]] = None,
        user_profile: Optional[dict] = None
    ) -> str:
        """Build the final prompt for Module 4 (Response Generator)"""
        
        # Build conversation context
        conversation_context = ""
        if history and len(history) > 0:
            # Include last 5 exchanges for context
            recent = history[-10:] if len(history) > 10 else history
            conversation_context = "\n\nConversation history:\n"
            for msg in recent:
                prefix = "User" if msg.role == "user" else "Nyx"
                conversation_context += f"{prefix}: {msg.content}\n"
        
        # User profile context (if available)
        profile_context = ""
        if user_profile:
            name = user_profile.get("name", "")
            if name:
                profile_context = f"\nUser's name: {name}"
        
        # Risk-based guidance
        risk_guidance = ""
        if analysis.risk_score >= 8:
            risk_guidance = "\n\nIMPORTANT: User is in crisis. Be extremely gentle. Validate their pain. Strongly encourage professional help. Do NOT try to solve their problems."
        elif analysis.risk_score >= 6:
            risk_guidance = "\n\nNote: User is struggling significantly. Offer extra support. Gently suggest talking to someone if appropriate."
        elif analysis.risk_score >= 4:
            risk_guidance = "\n\nNote: User is having a tough time. Be warm and validating."
        
        # Assemble final prompt
        prompt = f"""You are Nyx, a kind, warm AI companion and friend.{profile_context}

Current user message: "{message}"

Analysis from emotional engine:
- Primary emotion: {analysis.primary_emotion}
- Intent: {analysis.intent}
- Risk level: {analysis.crisis_level} (score: {analysis.risk_score}/10)
- Key concerns: {', '.join(analysis.key_concerns)}
- Suggested approach: {analysis.suggested_strategy}{risk_guidance}{conversation_context}

Your role:
- Listen and validate feelings
- Offer gentle, non-clinical support
- Never diagnose or give medical advice
- Stay hopeful but realistic
- Be concise (max 3 short paragraphs)

Generate a warm, empathetic response:"""
        
        return prompt
    
    def build_analysis_prompt(self, message: str, history: Optional[List[ChatMessage]] = None) -> str:
        """Build prompt for Module 1 (Analyzer)"""
        
        history_context = ""
        if history and len(history) > 0:
            recent = history[-5:]
            history_context = "\n\nRecent conversation:\n" + "\n".join([
                f"{msg.role}: {msg.content}" for msg in recent
            ])
        
        prompt = f"""Analyze the user's message for emotional content and risk assessment.

User message: "{message}"{history_context}

Return ONLY valid JSON:
{{
    "primary_emotion": "anxious|sad|angry|hopeless|overwhelmed|neutral|hopeful|grateful",
    "sentiment_score": -0.8,
    "intent": "venting|seeking_advice|asking_question|crisis_signal|general_chat",
    "crisis_level": "none|low|medium|high|crisis",
    "risk_score": 0-10,
    "key_concerns": ["concern1", "concern2"],
    "suggested_strategy": "how to respond"
}}

Crisis indicators (crisis_level = "crisis"):
- Suicidal ideation, self-harm intent
- "Want to die", "end it all", "can't go on", "no point living"
- Explicit plans or means mentioned

Be conservative. Better to flag than miss."""
        
        return prompt