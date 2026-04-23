import re
from typing import Tuple

from backend.models.analysis import RiskAssessment


class PostProcessor:
    """Module 5: Final safety layer and formatting."""

    PROBLEMATIC_PATTERNS = [
        (r"I am (?:a )?therapist", "I'm an AI companion, not a therapist"),
        (r"I am (?:a )?doctor", "I'm an AI companion, not a medical professional"),
        (
            r"You (?:have|are suffering from) (?:depression|anxiety|bipolar|PTSD|OCD)",
            "I hear that you're going through a difficult time",
        ),
        (r"Diagnosis[:\s]", ""),
        (r"Prescription[:\s]", ""),
        (r"Medication[:\s]", ""),
    ]

    def __init__(self):
        self.disclaimer = (
            "I'm an AI companion, not a therapist. For serious concerns, "
            "please reach out to a mental health professional."
        )
        self.crisis_disclaimer = (
            "Please reach out to a crisis helpline immediately. You don't have to go through this alone."
        )

    def process(self, response: str, risk_assessment: RiskAssessment) -> Tuple[str, bool]:
        """
        Process and sanitize the AI response.

        Returns:
            Tuple of (final_text, disclaimer_added)
        """
        text = response.strip()

        for pattern, replacement in self.PROBLEMATIC_PATTERNS:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        text = self._format_text(text)
        text = self._enforce_concise_style(text)

        if risk_assessment.risk_level == "crisis":
            disclaimer_added = False
        elif risk_assessment.risk_level in ["high", "medium"]:
            text = self._add_disclaimer(text, gentle=True)
            disclaimer_added = True
        else:
            disclaimer_added = False

        return text, disclaimer_added

    def _enforce_concise_style(self, text: str) -> str:
        """Keep replies concise but not truncated."""
        if not text:
            return text

        # Only truncate if extremely long (over 200 words)
        words = text.split()
        if len(words) > 200:
            text = " ".join(words[:200]).rstrip(",;:-") + "..."

        return text

    def _format_text(self, text: str) -> str:
        """Clean up formatting."""
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"^(nyx|assistant)\s*:\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"[ \t]{2,}", " ", text)
        text = re.sub(r"\.(\w)", r". \1", text)
        text = re.sub(r"([?!]){2,}", r"\1", text)
        text = re.sub(r"\s+([,.;!?])", r"\1", text)
        return text.strip()

    def _add_disclaimer(self, text: str, gentle: bool = False) -> str:
        """Add an elevated-risk disclaimer when needed."""
        if "not a therapist" in text.lower() or "not a professional" in text.lower():
            return text

        if gentle:
            disclaimer = (
                "\n\nReminder: I'm an AI companion, not a therapist. "
                "If you need extra support, reaching out to a mental health professional could help."
            )
        else:
            disclaimer = (
                "\n\nI'm an AI companion, not a therapist. For serious concerns, "
                "please reach out to a mental health professional."
            )

        return text + disclaimer

    def format_crisis_response(self) -> dict:
        """Format crisis mode response with demo helplines."""
        return {
            "crisis": True,
            "message": "We're really concerned about you right now. You're not alone.",
            "helplines": [
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
            ],
            "banner": "DEMO MODE - These are test numbers. Real version uses actual helplines.",
            "stay_option": "I'm here while you call",
        }
