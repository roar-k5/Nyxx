from typing import List, Optional
from datetime import datetime, timedelta
from backend.models.analysis import AnalysisResult, RiskAssessment

class RiskEngine:
    """Module 2: Risk assessment and temporal fusion"""
    
    def __init__(self):
        # In production, this would query Firebase for user's risk history
        # For demo, we use simple in-memory or passed context
        self.risk_history: dict = {}  # user_id -> list of risk scores
    
    def assess_risk(
        self, 
        analysis: AnalysisResult, 
        user_id: str = "anonymous",
        temporal_context: Optional[List[dict]] = None
    ) -> RiskAssessment:
        """
        Calculate final risk score with temporal context.
        
        Temporal fusion: If user had elevated risk recently, escalate faster.
        """
        base_score = analysis.risk_score
        crisis_level = analysis.crisis_level
        
        # Immediate crisis override
        if crisis_level == "crisis" or base_score >= 9:
            return RiskAssessment(
                risk_level="crisis",
                final_score=10,
                escalate=True,
                temporal_context="Immediate crisis detected"
            )
        
        # Temporal context adjustment
        temporal_bonus = 0
        context_note = ""
        
        if temporal_context and len(temporal_context) > 0:
            # Check recent risk scores (last 24 hours)
            recent_high_risks = [
                r for r in temporal_context 
                if r.get("score", 0) >= 6 and 
                datetime.now() - datetime.fromisoformat(r.get("timestamp", "2024-01-01")) < timedelta(hours=24)
            ]
            
            if len(recent_high_risks) >= 2:
                # Repeated distress pattern
                temporal_bonus = 1
                context_note = f"Pattern: {len(recent_high_risks)} elevated risk events in 24h"
            elif len(recent_high_risks) == 1:
                context_note = "Recent elevated risk (within 24h)"
        
        final_score = min(10, base_score + temporal_bonus)
        
        # Determine risk level
        if final_score >= 9:
            risk_level = "crisis"
            escalate = True
        elif final_score >= 7:
            risk_level = "high"
            escalate = False  # Still allow chat, but with caution
        elif final_score >= 5:
            risk_level = "medium"
            escalate = False
        else:
            risk_level = "low"
            escalate = False
        
        return RiskAssessment(
            risk_level=risk_level,
            final_score=final_score,
            escalate=escalate,
            temporal_context=context_note if context_note else None
        )
    
    def should_escalate_to_crisis(self, assessment: RiskAssessment) -> bool:
        """Determine if we should trigger crisis mode"""
        return assessment.escalate or assessment.final_score >= 9