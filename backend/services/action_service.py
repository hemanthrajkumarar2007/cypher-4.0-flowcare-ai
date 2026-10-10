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

        init_time = "2026-11-16 09:40"

        # Seed Action 1: Discharge paperwork clearance for blocked beds ED-06 & ED-07
        act1 = SimulatedAction(
            action_id="ACT-001",
            recommendation_id="REC-001",
            related_issue_id="ISSUE-BED-BLOCKED-DISCHARGE",
            action_type="Discharge Task Expedite",
            title="Deploy Discharge Liaison to Clear Blocked Beds ED-06 & ED-07",
            description=(
                "Expedite attending physician discharge summary counter-signature and coordinate "
                "diagnostic report clearance to immediately free up physically blocked beds ED-06 and ED-07."
            ),
            responsible_team="Discharge Coordination & Medical Records",
            target_department="Emergency",
            priority="Critical",
            status="Awaiting review",
            created_at=init_time,
            updated_at=init_time,
            created_by="FlowCare AI Agent"
        )
        self.actions[act1.action_id] = act1

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

        # Seed Action 2: STAT Diagnostic Escalation for CT Scans
        act2 = SimulatedAction(
            action_id="ACT-002",
            recommendation_id="REC-002",
            related_issue_id="ISSUE-DIAG-DELAY-EMER",
            action_type="Diagnostic Escalation",
            title="STAT Radiology Escalation for Overdue CT Scans T0001 & T0002",
            description=(
                "Alert Radiology duty lead to fast-track verification of CT Scans (T0001 for P1006, "
                "T0002 for P1007) overdue by 3 hours, currently holding up Emergency discharge disposition."
            ),
            responsible_team="Radiology & Central Laboratory Operations",
            target_department="Emergency",
            priority="Critical",
            status="Awaiting review",
            created_at="2026-11-16 09:45",
            updated_at="2026-11-16 09:45",
            created_by="FlowCare AI Agent"
        )
        self.actions[act2.action_id] = act2

        self.audit_log.append(AuditLogEntry(
            audit_id=f"AUD-{self._audit_seq:03d}",
            action_id=act2.action_id,
            previous_status="None",
            new_status="Awaiting review",
            timestamp="2026-11-16 09:45",
            reviewer_label="FlowCare AI Agent",
            notes="Automated diagnostic delay escalation queued for clinical lead review."
        ))
        self._audit_seq += 1

        # Seed Action 3: Emergency Evening Shift Float Staffing Call-In
        act3 = SimulatedAction(
            action_id="ACT-003",
            recommendation_id="REC-003",
            related_issue_id="ISSUE-STAFF-SHORTAGE-EM-EVE",
            action_type="Staff Shortage Call-In",
            title="Mobilize On-Call Emergency Doctor & 2 Float Nurses for Evening Shift (14–20)",
            description=(
                "Dr. Rahul Iyer is recorded on leave for the 14–20 shift. Request immediate deployment of an "
                "on-call emergency physician and 2 float nurses to prevent acute handover bottleneck."
            ),
            responsible_team="Hospital Rostering & Emergency Leadership",
            target_department="Emergency",
            priority="Critical",
            status="Awaiting review",
            created_at="2026-11-16 09:50",
            updated_at="2026-11-16 09:50",
            created_by="FlowCare AI Agent"
        )
        self.actions[act3.action_id] = act3

        self.audit_log.append(AuditLogEntry(
            audit_id=f"AUD-{self._audit_seq:03d}",
            action_id=act3.action_id,
            previous_status="None",
            new_status="Awaiting review",
            timestamp="2026-11-16 09:50",
            reviewer_label="FlowCare AI Agent",
            notes="Staffing deficit mitigation action queued for supervisor approval."
        ))
        self._audit_seq += 1

        self._action_seq = 4

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
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
            priority=req.priority or "High",
            status="Awaiting review",
            created_at=now,
            updated_at=now,
            created_by="FlowCare AI Agent",
            review_notes=req.notes
        )
        self.actions[action_id] = action

        self.audit_log.append(AuditLogEntry(
            audit_id=f"AUD-{self._audit_seq:03d}",
            action_id=action_id,
            previous_status="None",
            new_status="Awaiting review",
            timestamp=now,
            reviewer_label="FlowCare AI Agent",
            notes=f"Created task from recommendation: {req.proposed_action[:80]}"
        ))
        self._audit_seq += 1
        return action

    def review_action(self, action_id: str, review_req: ActionReviewRequest) -> SimulatedAction:
        """Reviews an action (Approve or Reject). Transitions status and logs in audit log."""
        action = self.actions.get(action_id)
        if not action:
            raise KeyError(f"Action '{action_id}' not found.")

        if action.status not in ("Awaiting review", "Pending review"):
            raise ValueError(f"Action '{action_id}' cannot be reviewed from current status '{action.status}'.")

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prev_status = action.status
        new_status = "Approved" if review_req.status.lower() == "approved" else "Rejected"

        action.status = new_status
        action.updated_at = now
        action.reviewed_by = review_req.reviewer_label
        action.review_notes = review_req.notes

        self.audit_log.append(AuditLogEntry(
            audit_id=f"AUD-{self._audit_seq:03d}",
            action_id=action_id,
            previous_status=prev_status,
            new_status=new_status,
            timestamp=now,
            reviewer_label=review_req.reviewer_label,
            notes=review_req.notes or f"Action {new_status.lower()} by authorized demo operator."
        ))
        self._audit_seq += 1
        return action

    def complete_action(self, action_id: str, comp_req: ActionCompleteRequest) -> SimulatedAction:
        """Marks an approved simulated action as Completed and appends an audit entry."""
        action = self.actions.get(action_id)
        if not action:
            raise KeyError(f"Action '{action_id}' not found.")

        if action.status != "Approved":
            raise ValueError(f"Action '{action_id}' cannot be completed because its status is '{action.status}' (must be 'Approved').")

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prev_status = action.status

        action.status = "Completed"
        action.updated_at = now
        action.completed_at = now

        self.audit_log.append(AuditLogEntry(
            audit_id=f"AUD-{self._audit_seq:03d}",
            action_id=action_id,
            previous_status=prev_status,
            new_status="Completed",
            timestamp=now,
            reviewer_label=comp_req.reviewer_label,
            notes=comp_req.notes or "Simulated task completed successfully."
        ))
        self._audit_seq += 1
        return action

    def get_audit_log(self, action_id: Optional[str] = None) -> List[AuditLogEntry]:
        """Returns the full audit log, optionally filtered by action ID."""
        if action_id:
            return [e for e in self.audit_log if e.action_id == action_id]
        return self.audit_log


action_service = ActionService()
