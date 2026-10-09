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
            if issue.issue_type in ("BED_SHORTAGE_OR_BLOCK", "STUCK_DISCHARGE"):
                if "BLOCKED" in issue.issue_id or "STUCK" in issue.issue_id:
                    recommendations.append(Recommendation(
                        recommendation_id=f"REC-{rec_counter:03d}",
                        related_issue_id=issue.issue_id,
                        category="Discharge task prioritization",
                        proposed_action=(
                            "Deploy a dedicated Discharge Liaison to fast-track insurance TPA pre-authorization "
                            "and obtain immediate attending physician counter-signature on discharge summaries for beds EMERG-03 and EMERG-04."
                        ),
                        reason=(
                            "Two beds are physically blocked purely by administrative paperwork, directly constricting "
                            "emergency intake and causing 95+ minute triage wait times."
                        ),
                        supporting_evidence=issue.evidence,
                        responsible_team="Discharge Coordination & Patient Billing Desk",
                        priority="Critical",
                        review_status="Pending"
                    ))
                    rec_counter += 1

                    recommendations.append(Recommendation(
                        recommendation_id=f"REC-{rec_counter:03d}",
                        related_issue_id=issue.issue_id,
                        category="Bed-management review",
                        proposed_action=(
                            "Pre-alert Housekeeping unit to stage sanitization kits for beds EMERG-03 and EMERG-04 "
                            "to initiate immediate cleaning the moment paperwork clears."
                        ),
                        reason=(
                            "Minimizes bed cleaning turnaround time so newly admitted emergency patients can transition "
                            "into beds without idle delays."
                        ),
                        supporting_evidence=[
                            "Beds EMERG-03 and EMERG-04 will require rapid turnover to absorb waiting patients."
                        ],
                        responsible_team="Hospital Housekeeping & Environmental Services",
                        priority="High",
                        review_status="Pending"
                    ))
                    rec_counter += 1

                elif "IDLE" in issue.issue_id:
                    recommendations.append(Recommendation(
                        recommendation_id=f"REC-{rec_counter:03d}",
                        related_issue_id=issue.issue_id,
                        category="Bed-management review",
                        proposed_action=(
                            "Authorise Bed Management supervisor to review stable emergency admission candidates for "
                            "transfer into available beds in General Ward (GEN-05, GEN-06, GEN-09)."
                        ),
                        reason="Multiple General beds remain idle while Emergency Ward is constrained.",
                        supporting_evidence=issue.evidence,
                        responsible_team="Bed Allocation & Patient Placement Unit",
                        priority="Medium",
                        review_status="Pending"
                    ))
                    rec_counter += 1

            elif issue.issue_type == "LONG_WAITING_TIME":
                recommendations.append(Recommendation(
                    recommendation_id=f"REC-{rec_counter:03d}",
                    related_issue_id=issue.issue_id,
                    category="Department capacity review",
                    proposed_action=(
                        f"Initiate urgent triage intake review in {issue.affected_department}. "
                        "Open secondary fast-track assessment cubicle to manage lower-acuity arrivals."
                    ),
                    reason=f"Measured patient wait times in {issue.affected_department} exceed acceptable baseline.",
                    supporting_evidence=issue.evidence,
                    responsible_team="Emergency & Outpatient Operations Board",
                    priority="High" if issue.urgency == "Critical" else "Medium",
                    review_status="Pending"
                ))
                rec_counter += 1

            elif issue.issue_type == "DELAYED_DIAGNOSTICS":
                recommendations.append(Recommendation(
                    recommendation_id=f"REC-{rec_counter:03d}",
                    related_issue_id=issue.issue_id,
                    category="Diagnostic escalation",
                    proposed_action=(
                        "Transmit STAT diagnostic escalation alert to Central Laboratory and Imaging duty lead. "
                        "Prioritize immediate verification of Troponin-T (DIAG-101) and Head CT (DIAG-103)."
                    ),
                    reason=(
                        "Critical emergency clinical decisions are suspended awaiting late diagnostic reports, "
                        "causing patient observation beds to remain occupied."
                    ),
                    supporting_evidence=issue.evidence,
                    responsible_team="Central Laboratory & Radiology Duty Desk",
                    priority="Critical" if issue.urgency == "Critical" else "High",
                    review_status="Pending"
                ))
                rec_counter += 1

            elif issue.issue_type == "STAFF_WORKLOAD_IMBALANCE":
                if "SHORTAGE" in issue.issue_id:
                    recommendations.append(Recommendation(
                        recommendation_id=f"REC-{rec_counter:03d}",
                        related_issue_id=issue.issue_id,
                        category="Staff shortage alert",
                        proposed_action=(
                            "Issue immediate staff shortage notification to Nursing Director and Emergency Department Roster Lead. "
                            "Call in 1 on-call emergency physician and 2 nursing staff for the incoming Evening shift."
                        ),
                        reason="Evening shift in Emergency has only 1 doctor scheduled, risking severe care bottleneck.",
                        supporting_evidence=issue.evidence,
                        responsible_team="Hospital Rostering & Nursing Administration",
                        priority="High",
                        review_status="Pending"
                    ))
                    rec_counter += 1
                else:
                    recommendations.append(Recommendation(
                        recommendation_id=f"REC-{rec_counter:03d}",
                        related_issue_id=issue.issue_id,
                        category="Staffing review or proposed reallocation",
                        proposed_action=(
                            "Request administrative operations review to reassign support staff from low-workload outpatient "
                            "clinics (Dermatology) to help with triage intake documentation in acute departments."
                        ),
                        reason="Cross-department workload disparity between acute care and outpatient clinics.",
                        supporting_evidence=issue.evidence,
                        responsible_team="Hospital Operations Administration",
                        priority="Medium",
                        review_status="Pending"
                    ))
                    rec_counter += 1

            elif issue.issue_type == "APPOINTMENT_ANOMALY":
                if "OVERLOAD" in issue.issue_id:
                    recommendations.append(Recommendation(
                        recommendation_id=f"REC-{rec_counter:03d}",
                        related_issue_id=issue.issue_id,
                        category="Appointment rescheduling recommendation",
                        proposed_action=(
                            f"Contact patients in the overbooked slot ({issue.details.get('slot_time')}) in {issue.affected_department} "
                            "to offer prioritized voluntary reschedule slots in subsequent clinic sessions."
                        ),
                        reason="Multiple simultaneous bookings exceed physician consultation capacity.",
                        supporting_evidence=issue.evidence,
                        responsible_team="Outpatient Scheduling & Patient Access",
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
                        f"Deploy Patient Relations Liaison to {issue.affected_department} waiting area to address "
                        "patient family grievances regarding waiting times and diagnostic delays."
                    ),
                    reason="High severity complaints logged by patients actively waiting in the department.",
                    supporting_evidence=issue.evidence,
                    responsible_team="Patient Relations & Quality Assurance",
                    priority="High",
                    review_status="Pending"
                ))
                rec_counter += 1

        return recommendations


recommendation_service = RecommendationService()
