import re
from dataclasses import dataclass
from typing import List, Optional

from backend.models.analysis import ChatMessage


@dataclass
class SafetySignals:
    crisis: bool
    self_harm: bool
    interpersonal_violence: bool
    bullying: bool
    harassment: bool


class SafetyDetector:
    """Centralized safety signal detection for chat messages."""

    def _combined_text(self, message: str, history: Optional[List[ChatMessage]] = None) -> str:
        parts = [message.lower()]
        if history:
            parts.extend(msg.content.lower() for msg in history[-6:] if msg.role == "user")
        return "\n".join(parts)

    def detects_self_harm(self, message: str, history: Optional[List[ChatMessage]] = None) -> bool:
        combined = self._combined_text(message, history)
        normalized = re.sub(r"[^a-z0-9\s']", " ", combined)
        normalized = re.sub(r"\s+", " ", normalized).strip()

        direct_phrases = [
            "kill myself",
            "suicide",
            "end my life",
            "want to die",
            "hurt myself",
            "self harm",
            "no point living",
            "better off dead",
            "cant go on",
            "can't go on",
            "end it all",
            "end everything",
            "end evrything",
            "i wanna die",
            "i wana die",
            "i wanan die",
        ]
        if any(phrase in normalized for phrase in direct_phrases):
            return True

        regex_patterns = [
            r"\bi\s+wan+\w*\s+(to\s+)?die\b",
            r"\bi\s+want\s+to\s+die\b",
            r"\bi\s+want\s+to\s+end\s+(it\s+all|everything|evrything|my\s+life)\b",
            r"\bi\s+am\s+going\s+to\s+(kill|hurt)\s+myself\b",
            r"\b(end|ending)\s+(everything|evrything|it\s+all|my\s+life)\b",
        ]
        if any(re.search(pattern, normalized) for pattern in regex_patterns):
            return True

        if re.search(r"\b(die|dead)\b", normalized):
            intent_context = [
                r"\b(i|im|i'm)\b",
                r"\bwant\b|\bgonna\b|\bgoing to\b|\bthinking\b",
                r"\b(end|kill|hurt)\b|\bmyself\b|\blife\b|\beverything\b|\bevrything\b",
            ]
            return all(re.search(pattern, normalized) for pattern in intent_context)

        return False

    def detects_interpersonal_violence(
        self,
        message: str,
        history: Optional[List[ChatMessage]] = None,
    ) -> bool:
        combined = self._combined_text(message, history)

        direct_patterns = [
            r"\bcan i beat (him|her|them|someone)\b",
            r"\bi want to (hit|hurt|beat|attack|fight) (him|her|them|someone)\b",
            r"\bshould i (hit|hurt|beat|attack|fight) (him|her|them|someone)\b",
            r"\bi(?:'| a)?m going to (hit|hurt|beat|attack|fight) (him|her|them|someone)\b",
            r"\bpunch (him|her|them|someone)\b",
            r"\bslap (him|her|them|someone)\b",
            r"\bkill (him|her|them)\b",
        ]
        escalation_cues = [
            "ragebait",
            "rage bait",
            "ragebating",
            "they keep pushing me",
            "they won't stop",
            "i'm gonna snap",
            "everyone sucks",
        ]
        return any(re.search(pattern, combined) for pattern in direct_patterns) or any(
            cue in combined for cue in escalation_cues
        )

    def detects_bullying(self, message: str, history: Optional[List[ChatMessage]] = None) -> bool:
        combined = self._combined_text(message, history)
        bullying_patterns = [
            r"\bthey (keep )?(bully|bullying) me\b",
            r"\bi am being bullied\b",
            r"\bpeople at (school|class|work) (mock|tease|target) me\b",
            r"\bthey (laugh at|make fun of) me\b",
            r"\bgetting picked on\b",
        ]
        return any(re.search(pattern, combined) for pattern in bullying_patterns)

    def detects_harassment(self, message: str, history: Optional[List[ChatMessage]] = None) -> bool:
        combined = self._combined_text(message, history)
        harassment_patterns = [
            r"\b(i am|i'm) being harassed\b",
            r"\bhe (keeps|keep) (touching|messaging|following) me\b",
            r"\bthey (wont|won't) leave me alone\b",
            r"\bunsafe around (him|her|them)\b",
            r"\bsexual harass(ment)?\b",
            r"\bstalking me\b",
        ]
        return any(re.search(pattern, combined) for pattern in harassment_patterns)

    def detect(self, message: str, history: Optional[List[ChatMessage]] = None) -> SafetySignals:
        self_harm = self.detects_self_harm(message, history)
        return SafetySignals(
            crisis=self_harm,
            self_harm=self_harm,
            interpersonal_violence=self.detects_interpersonal_violence(message, history),
            bullying=self.detects_bullying(message, history),
            harassment=self.detects_harassment(message, history),
        )
