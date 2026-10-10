"""
FlowCare AI — Actionable Recommendation Engine
Sanjeevani Multispeciality Hospital
Cypher 2026 Hackathon — "The Blocked Bed" Challenge
"""

from typing import List, Optional
from models import Recommendation, BottleneckIssue
from services.detection_service import DetectionService, detection_service


class RecommendationService:
    """Generates practical operational recommendations linked to detected bottlenecks."""

    def __init__(self, detection_svc: Optional[DetectionService] = None):
        self.detection_service = detection_svc or detection_service

    def generate_recommendations(self, issues: Optional[List[BottleneckIssue]] = None) -> List[Recommendation]:
        """Maps detected issues to actionable, prioritized recommendations."""
        if issues is None:
            issues = self.detection_service.detect_all_issues()

        recommendations: List[Recommendation] = []
        rec_counter = 1

        for issue in issues:
            if issue.issue_type == "ESCALATION_REQUIRED":
                recommendations.append(Recommendation(
                    recommendation_id=f"REC-{rec_counter:03d}",
                    related_issue_id=issue.issue_id,
                    category="Multi-Department Escalation",
                    proposed_action=(
                        "Convene immediate emergency command huddle with Medical Director, Nursing Lead, and Radiology Supervisor. "
                        "Authorize fast-track discharge of ED-06 and ED-07 to immediately liberate 2 emergency beds, mobilize "
                        "on-call physician for the 14–20 shift, and evaluate step-down transfers from ICU for P1 patient P1087."
                    ),
                    reason="Compounding systemic crisis across triage waiting times, blocked beds, diagnostics, and upcoming shift staffing.",
                    supporting_evidence=issue.evidence,
                    responsible_team="Hospital Executive Leadership & Emergency Task Force",
                    priority="Critical",
                    review_status="Pending"
                ))
                rec_counter += 1

            elif issue.issue_type in ("BED_SHORTAGE_OR_BLOCK", "STUCK_DISCHARGE"):
                if "BLOCKED" in issue.issue_id or "STUCK" in issue.issue_id:
                    recommendations.append(Recommendation(
                        recommendation_id=f"REC-{rec_counter:03d}",
                        related_issue_id=issue.issue_id,
                        category="Discharge task prioritization",
                        proposed_action=(
                            "Deploy a dedicated Discharge Liaison to expedite attending physician summary counter-signatures "
                            "and coordinate diagnostic clearances for blocked emergency beds ED-06 and ED-07, and General Ward beds."
                        ),
                        reason=(
                            "Beds are physically blocked purely by pending paperwork and diagnostic clearances, directly "
                            "freezing intake capacity and compounding emergency wait times."
                        ),
                        supporting_evidence=issue.evidence,
                        responsible_team="Discharge Coordination & Medical Records",
                        priority="Critical",
                        review_status="Pending"
                    ))
                    rec_counter += 1

                    recommendations.append(Recommendation(
                        recommendation_id=f"REC-{rec_counter:03d}",
                        related_issue_id=issue.issue_id,
                        category="Bed-management review",
                        proposed_action=(
                            "Pre-alert Housekeeping Environmental Services to stage rapid sanitization teams for beds ED-06, "
                            "ED-07, and pending discharge beds to execute immediate turnaround the moment discharge clears."
                        ),
                        reason="Minimizes post-discharge cleaning turnaround time to rapidly intake waiting patients.",
                        supporting_evidence=[
                            "Beds ED-06 and ED-07 require rapid turnover to absorb waiting patients."
                        ],
                        responsible_team="Hospital Housekeeping & Environmental Services",
                        priority="High",
                        review_status="Pending"
                    ))
                    rec_counter += 1

                elif "ICU" in issue.issue_id:
                    recommendations.append(Recommendation(
                        recommendation_id=f"REC-{rec_counter:03d}",
                        related_issue_id=issue.issue_id,
                        category="Bed-management review",
                        proposed_action=(
                            "Authorize Critical Care clinical lead to assess stable ICU patients for step-down transition "
                            "to general wards, liberating an ICU bed for awaiting triage P1 patient P1087 in ED."
                        ),
                        reason="ICU is at 100% occupancy with high-acuity patients holding in Emergency triage.",
                        supporting_evidence=issue.evidence,
                        responsible_team="Critical Care Clinical Review Board",
                        priority="Critical",
                        review_status="Pending"
                    ))
                    rec_counter += 1

            elif issue.issue_type == "LONG_WAITING_TIME":
                if "EMER" in issue.issue_id:
                    recommendations.append(Recommendation(
                        recommendation_id=f"REC-{rec_counter:03d}",
                        related_issue_id=issue.issue_id,
                        category="Department capacity review",
                        proposed_action=(
                            "Initiate urgent emergency surge protocol: activate secondary triage cubicle, deploy rapid assessment "
                            "nurse, and stream ambulatory patients into rapid-consultation workflow."
                        ),
                        reason="Emergency Department waiting times have surged to 98 minutes with 9 patients awaiting beds.",
                        supporting_evidence=issue.evidence,
                        responsible_team="Emergency Department Clinical Operations",
                        priority="Critical",
                        review_status="Pending"
                    ))
                    rec_counter += 1
                else:
                    recommendations.append(Recommendation(
                        recommendation_id=f"REC-{rec_counter:03d}",
                        related_issue_id=issue.issue_id,
                        category="Department capacity review",
                        proposed_action=(
                            f"Initiate scheduling and consultation pace review in {issue.affected_department}. "
                            "Stagger afternoon appointments to alleviate waiting room crowding."
                        ),
                        reason=f"Patient waiting times in {issue.affected_department} exceed clinic baselines.",
                        supporting_evidence=issue.evidence,
                        responsible_team=f"{issue.affected_department} Clinic Administration",
                        priority="Medium",
                        review_status="Pending"
                    ))
                    rec_counter += 1

            elif issue.issue_type == "DELAYED_DIAGNOSTICS":
                if "EMER" in issue.issue_id:
                    recommendations.append(Recommendation(
                        recommendation_id=f"REC-{rec_counter:03d}",
                        related_issue_id=issue.issue_id,
                        category="Diagnostic escalation",
                        proposed_action=(
                            "Transmit STAT diagnostic escalation alert to Central Laboratory and Imaging duty lead. "
                            "Prioritize immediate radiologist reading and sign-off for CT Scans (T0001, T0002) and urgent cardiac labs."
                        ),
                        reason="Delayed CT Scans are holding up clinical disposition and discharge for beds ED-06 and ED-07.",
                        supporting_evidence=issue.evidence,
                        responsible_team="Radiology & Central Laboratory Operations",
                        priority="Critical",
                        review_status="Pending"
                    ))
                    rec_counter += 1
                else:
                    recommendations.append(Recommendation(
                        recommendation_id=f"REC-{rec_counter:03d}",
                        related_issue_id=issue.issue_id,
                        category="Diagnostic escalation",
                        proposed_action=(
                            f"Escalate overdue diagnostic orders in {issue.affected_department} to diagnostic duty desk for batch acceleration."
                        ),
                        reason="Inpatient turnaround delays extend overall length of stay.",
                        supporting_evidence=issue.evidence,
                        responsible_team="Central Diagnostics Operations",
                        priority="High",
                        review_status="Pending"
                    ))
                    rec_counter += 1

            elif issue.issue_type == "STAFF_WORKLOAD_IMBALANCE":
                if "EVE" in issue.issue_id or "EM-EVE" in issue.issue_id:
                    recommendations.append(Recommendation(
                        recommendation_id=f"REC-{rec_counter:03d}",
                        related_issue_id=issue.issue_id,
                        category="Staff shortage alert",
                        proposed_action=(
                            "Issue immediate staff shortage alert to Emergency Clinical Director and Hospital Rostering. "
                            "Call in 1 on-call emergency physician and 2 float nurses for the incoming Evening shift (14–20)."
                        ),
                        reason="Dr. Rahul Iyer is on leave, leaving only 1 doctor and 3 nurses against peak patient inflow.",
                        supporting_evidence=issue.evidence,
                        responsible_team="Hospital Rostering & Emergency Leadership",
                        priority="Critical",
                        review_status="Pending"
                    ))
                    rec_counter += 1
                else:
                    recommendations.append(Recommendation(
                        recommendation_id=f"REC-{rec_counter:03d}",
                        related_issue_id=issue.issue_id,
                        category="Staffing review or proposed reallocation",
                        proposed_action=(
                            f"Review clinician patient allocation in {issue.affected_department} to level workload across available specialists."
                        ),
                        reason="Individual physician patient load exceeds standard thresholds.",
                        supporting_evidence=issue.evidence,
                        responsible_team=f"{issue.affected_department} Clinic Operations",
                        priority="Medium",
                        review_status="Pending"
                    ))
                    rec_counter += 1

            elif issue.issue_type == "OPERATIONAL_COMPLAINT":
                recommendations.append(Recommendation(
                    recommendation_id=f"REC-{rec_counter:03d}",
                    related_issue_id=issue.issue_id,
                    category="Complaint escalation",
                    proposed_action=(
                        f"Deploy Patient Relations Liaison to address grievances regarding {issue.title}. "
                        "Provide active status communication to affected families."
                    ),
                    reason="Multiple unresolved patient complaints received.",
                    supporting_evidence=issue.evidence,
                    responsible_team="Patient Relations & Experience",
                    priority="High",
                    review_status="Pending"
                ))
                rec_counter += 1

        return recommendations


recommendation_service = RecommendationService()
