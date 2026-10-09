"""
FlowCare AI — Simulated Action & Audit Logging Service
Sanjeevani Multispeciality Hospital
Cypher 2026 Hackathon — "The Blocked Bed" Challenge
"""

from datetime import datetime
from typing import List, Optional, Dict
from models import (
    SimulatedAction,
    ActionCreateRequest,
    ActionReviewRequest,
    ActionCompleteRequest,
    AuditLogEntry,
)


class ActionService:
    """
    Manages the lifecycle of simulated tasks and alerts:
    Awaiting review -> Approved / Rejected -> Completed.
    Maintains an immutable historical audit log.
    """

    def __init__(self):
        self.actions: Dict[str, SimulatedAction] = {}
        self.audit_log: List[AuditLogEntry] = []
        self._action_seq = 1
        self._audit_seq = 1
        self.seed_initial_actions()

    def seed_initial_actions(self) -> None:
        """Seeds initial realistic simulated tasks for the Sanjeevani demonstration scenario."""
        self.actions.clear()
        self.audit_log.clear()
        self._action_seq = 1
        self._audit_seq = 1

        # Seed Action 1: Discharge paperwork clearance for blocked beds
        init_time = "2026-10-10T09:40:00"
        act1 = SimulatedAction(
            action_id="ACT-001",
            recommendation_id="REC-001",
            related_issue_id="ISSUE-BED-BLOCKED-DISCHARGE",
            action_type="Discharge Task Expedite",
            title="Deploy Discharge Liaison to Clear Blocked Beds EMERG-03 and EMERG-04",
            description=(
                "Expedite TPA insurance billing clearance and obtain attending physician discharge "
                "sign-off to free up physically blocked beds EMERG-03 and EMERG-04."
            ),
            responsible_team="Discharge Coordination & Patient Billing Desk",
            target_department="Emergency",
            priority="Critical",
            status="Awaiting review",
            created_at=init_time,
            updated_at=init_time,
            created_by="FlowCare AI Agent"
        )
        self.actions[act1.action_id] = act1

        # Initial audit log for ACT-001 creation
        self.audit_log.append(AuditLogEntry(
            audit_id=f"AUD-{self._audit_seq:03d}",
            action_id=act1.action_id,
            previous_status="None",
            new_status="Awaiting review",
            timestamp=init_time,
            reviewer_label="FlowCare AI Agent",
            notes="Automated operational recommendation converted to simulated action."
        ))
        self._audit_seq += 1

        # Seed Action 2: STAT Diagnostic Escalation
        act2 = SimulatedAction(
            action_id="ACT-002",
            recommendation_id="REC-004",
            related_issue_id="ISSUE-DIAG-DELAY-EMER",
            action_type="Diagnostic Escalation",
            title="Issue STAT Laboratory Escalation for Overdue Cardiac & Trauma Diagnostics",
            description=(
                "Alert Central Lab supervisor to fast-track verification of Troponin-T (DIAG-101) "
                "and CT Scan (DIAG-103) holding up Emergency patient dispositions."
            ),
            responsible_team="Central Laboratory & Radiology Duty Desk",
            target_department="Emergency",
            priority="Critical",
            status="Awaiting review",
            created_at="2026-10-10T09:45:00",
            updated_at="2026-10-10T09:45:00",
            created_by="FlowCare AI Agent"
        )
        self.actions[act2.action_id] = act2

        self.audit_log.append(AuditLogEntry(
            audit_id=f"AUD-{self._audit_seq:03d}",
            action_id=act2.action_id,
            previous_status="None",
            new_status="Awaiting review",
            timestamp="2026-10-10T09:45:00",
            reviewer_label="FlowCare AI Agent",
            notes="Automated operational recommendation converted to simulated action."
        ))
        self._audit_seq += 1
        self._action_seq = 3

    def get_actions(self, status: Optional[str] = None) -> List[SimulatedAction]:
        """Returns all simulated actions, optionally filtered by status."""
        action_list = list(self.actions.values())
        if status:
            action_list = [a for a in action_list if a.status.lower() == status.lower()]
        return action_list

    def get_action_by_id(self, action_id: str) -> Optional[SimulatedAction]:
        """Retrieves a single simulated action by ID."""
        return self.actions.get(action_id)

    def create_action(self, req: ActionCreateRequest) -> SimulatedAction:
        """Creates a new simulated action and logs creation in audit trail."""
        now = datetime.now().isoformat()
        action_id = f"ACT-{self._action_seq:03d}"
        self._action_seq += 1

        action = SimulatedAction(
            action_id=action_id,
            recommendation_id=req.recommendation_id,
            related_issue_id=req.related_issue_id,
            action_type=req.responsible_team,
            title=f"Task: {req.proposed_action[:60]}...",
            description=req.proposed_action,
            responsible_team=req.responsible_team,
            target_department=req.target_department,
            priority=req.priority,
            status="Awaiting review",
            created_at=now,
            updated_at=now,
            created_by="FlowCare AI Agent",
            review_notes=req.notes
        )
        self.actions[action_id] = action

        # Audit entry
        self.audit_log.append(AuditLogEntry(
            audit_id=f"AUD-{self._audit_seq:03d}",
            action_id=action_id,
            previous_status="None",
            new_status="Awaiting review",
            timestamp=now,
            reviewer_label="FlowCare AI Agent",
            notes=f"Created simulated action for recommendation {req.recommendation_id}."
        ))
        self._audit_seq += 1

        return action

    def review_action(self, action_id: str, review_req: ActionReviewRequest) -> SimulatedAction:
        """
        Reviews a simulated action (Approved or Rejected) by authorized demo operator.
        Validates state transition and logs to audit log.
        """
        action = self.actions.get(action_id)
        if not action:
            raise KeyError(f"Action {action_id} not found.")

        target_status = review_req.status.capitalize()
        if target_status not in ("Approved", "Rejected"):
            raise ValueError(f"Invalid review status: '{review_req.status}'. Must be 'Approved' or 'Rejected'.")

        if action.status != "Awaiting review":
            raise ValueError(f"Action {action_id} cannot be reviewed because current status is '{action.status}'.")

        now = datetime.now().isoformat()
        prev_status = action.status
        action.status = target_status
        action.reviewed_by = review_req.reviewer_label
        action.review_notes = review_req.notes
        action.updated_at = now

        # Record in audit log
        self.audit_log.append(AuditLogEntry(
            audit_id=f"AUD-{self._audit_seq:03d}",
            action_id=action_id,
            previous_status=prev_status,
            new_status=target_status,
            timestamp=now,
            reviewer_label=review_req.reviewer_label,
            notes=f"Action reviewed by {review_req.reviewer_label}. Notes: {review_req.notes or 'None'}"
        ))
        self._audit_seq += 1

        return action

    def complete_action(self, action_id: str, comp_req: ActionCompleteRequest) -> SimulatedAction:
        """
        Marks an approved simulated action as Completed.
        Validates state transition and logs to audit log.
        """
        action = self.actions.get(action_id)
        if not action:
            raise KeyError(f"Action {action_id} not found.")

        if action.status != "Approved":
            raise ValueError(f"Action {action_id} cannot be completed because current status is '{action.status}'. Only 'Approved' actions can be marked Completed.")

        now = datetime.now().isoformat()
        prev_status = action.status
        action.status = "Completed"
        action.completed_at = now
        action.updated_at = now
        if comp_req.notes:
            action.review_notes = (action.review_notes or "") + f" | Completion notes: {comp_req.notes}"

        # Record in audit log
        self.audit_log.append(AuditLogEntry(
            audit_id=f"AUD-{self._audit_seq:03d}",
            action_id=action_id,
            previous_status=prev_status,
            new_status="Completed",
            timestamp=now,
            reviewer_label=comp_req.reviewer_label,
            notes=f"Simulated action completed by {comp_req.reviewer_label}. Notes: {comp_req.notes or 'None'}"
        ))
        self._audit_seq += 1

        return action

    def get_audit_log(self, action_id: Optional[str] = None) -> List[AuditLogEntry]:
        """Returns the audit log, optionally filtered by action_id."""
        if action_id:
            return [e for e in self.audit_log if e.action_id == action_id]
        return list(self.audit_log)


action_service = ActionService()
