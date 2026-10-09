"""
FlowCare AI — Priority Scoring Engine
Sanjeevani Multispeciality Hospital

Operational Prioritization Formula:
- Base Urgency Points (40 max): Critical=40, High=30, Medium=20, Low=10
- Base Operational Impact Points (40 max): Critical=40, High=30, Medium=20, Low=10
- Context Modifiers (20 max):
    * Escalation triggered: +10 pts
    * High duration / severe queue delay: +5 to +10 pts
- Priority Score = min(100, max(0, urgency_pts + impact_pts + modifiers))
- Priority Level Mapping:
    * 85 - 100: "Critical"
    * 65 - 84: "High"
    * 40 - 64: "Medium"
    * 0 - 39: "Low"

Notice: This is an operational hospital workflow prioritization system, NOT a clinical risk score.
"""

from typing import Tuple


class PriorityService:
    """Calculates transparent, explainable operational priority scores."""

    URGENCY_WEIGHTS = {
        "critical": 40,
        "high": 30,
        "medium": 20,
        "low": 10,
    }

    IMPACT_WEIGHTS = {
        "critical": 40,
        "high": 30,
        "medium": 20,
        "low": 10,
    }

    @classmethod
    def calculate_priority(
        cls,
        urgency: str,
        operational_impact: str,
        escalation_required: bool = False,
        delay_or_volume_modifier: int = 0
    ) -> Tuple[int, str]:
        """
        Calculates priority score (0-100) and priority level.
        Returns: (priority_score, priority_level)
        """
        urg_pts = cls.URGENCY_WEIGHTS.get(urgency.lower(), 20)
        imp_pts = cls.IMPACT_WEIGHTS.get(operational_impact.lower(), 20)
        
        bonus = 0
        if escalation_required:
            bonus += 10
        bonus += min(10, max(0, delay_or_volume_modifier))

        total_score = min(100, max(0, urg_pts + imp_pts + bonus))

        if total_score >= 85:
            level = "Critical"
        elif total_score >= 65:
            level = "High"
        elif total_score >= 40:
            level = "Medium"
        else:
            level = "Low"

        return total_score, level


priority_service = PriorityService()
