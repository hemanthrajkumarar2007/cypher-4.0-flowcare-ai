"""
FlowCare AI — Data & Domain Models
Sanjeevani Multispeciality Hospital
Cypher 2026 Hackathon — "The Blocked Bed" Challenge
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ============================================================================
# Core Synthetic Hospital Data Models
# ============================================================================

class Patient(BaseModel):
    """Hospital patient record."""
    patient_id: str = Field(..., description="Unique patient identifier")
    age_group: str = Field(..., description="Age bracket: Pediatric, Adult, Middle-Aged, Geriatric")
    department: str = Field(..., description="Primary attending department")
    visit_type: str = Field(..., description="Emergency, Outpatient, Inpatient, Follow-up")
    status: str = Field(..., description="Waiting, In Consultation, Admitted, Under Observation, Discharged")


class Appointment(BaseModel):
    """Outpatient or consultation appointment record."""
    appointment_id: str = Field(..., description="Unique appointment identifier")
    doctor: str = Field(..., description="Attending physician name")
    department: str = Field(..., description="Hospital department")
    datetime: str = Field(..., description="Scheduled appointment datetime in ISO 8601")
    status: str = Field(..., description="scheduled, completed, cancelled, or no-show")
    waiting_time: int = Field(..., ge=0, description="Waiting time in minutes")


class Bed(BaseModel):
    """Hospital bed unit representation."""
    bed_id: str = Field(..., description="Unique bed identifier")
    ward: str = Field(..., description="Ward name e.g. Emergency Ward, ICU, General Male")
    bed_type: str = Field(..., description="General, Emergency, ICU, Step-down")
    occupancy: str = Field(..., description="Occupied, Unoccupied")
    availability: str = Field(..., description="Available, Occupied, Blocked, Cleaning")
    admission_discharge_status: str = Field(
        ...,
        description="Ready, Occupied, Pending Discharge, Discharge Paperwork Blocked, Cleaning Required"
    )
    current_admission_id: Optional[str] = Field(None, description="Linked admission ID if occupied or blocked")
    blocked_reason: Optional[str] = Field(None, description="Reason if bed is blocked")


class Staff(BaseModel):
    """Hospital clinical and operational personnel."""
    staff_id: str = Field(..., description="Unique staff identifier")
    name: str = Field(..., description="Staff member full name")
    role: str = Field(..., description="Doctor, Nurse, Support Staff, Technician")
    department: str = Field(..., description="Assigned clinical or operational department")
    shift: str = Field(..., description="Morning, Evening, Night")
    availability: str = Field(..., description="Available, On Duty, On Break, Unavailable, On Leave")
    workload: str = Field(..., description="Low, Normal, High, Critical")


class Diagnostic(BaseModel):
    """Laboratory and diagnostic imaging request record."""
    test_id: str = Field(..., description="Unique diagnostic order identifier")
    test: str = Field(..., description="Test name e.g. CBC, Troponin-T, Chest X-Ray")
    patient: str = Field(..., description="Patient ID referencing a valid patient")
    department: str = Field(..., description="Ordering department")
    status: str = Field(..., description="pending, in-progress, completed, overdue")
    requested_time: str = Field(..., description="Order timestamp in ISO 8601")
    expected_completion: str = Field(..., description="Expected turnaround timestamp in ISO 8601")
    completed_time: Optional[str] = Field(None, description="Actual completion timestamp if finished")


class Admission(BaseModel):
    """Inpatient hospital admission record."""
    admission_id: str = Field(..., description="Unique admission record identifier")
    patient_id: str = Field(..., description="Patient ID referencing a valid patient")
    admission_time: str = Field(..., description="Admission timestamp in ISO 8601")
    department: str = Field(..., description="Admitting department")
    ward: str = Field(..., description="Assigned ward")
    bed_id: Optional[str] = Field(None, description="Assigned bed ID")
    expected_discharge: str = Field(..., description="Target discharge timestamp in ISO 8601")
    status: str = Field(..., description="Active, Discharging, Discharged")


class Discharge(BaseModel):
    """Inpatient discharge request and clearance workflow."""
    discharge_id: str = Field(..., description="Unique discharge tracking identifier")
    admission_id: str = Field(..., description="Admission ID referencing a valid admission")
    patient_id: str = Field(..., description="Patient ID referencing a valid patient")
    request: str = Field(..., description="Pending, Approved, In Review")
    pending_tasks: List[str] = Field(default_factory=list, description="Pending clearance tasks")
    medication_status: str = Field(
        ...,
        description="Operational status only: Pending Verification, Completed, Ready for Reconciliation"
    )
    document_status: str = Field(..., description="Incomplete, Pending Signature, Cleared")
    discharge_initiated_at: str = Field(..., description="Discharge request timestamp in ISO 8601")


class Feedback(BaseModel):
    """Patient and family operational feedback or complaint."""
    feedback_id: str = Field(..., description="Unique feedback record identifier")
    complaint: str = Field(..., description="Descriptive feedback or complaint statement")
    category: str = Field(..., description="Waiting Time, Bed Shortage, Diagnostics Delay, Staffing, Facility")
    department: Optional[str] = Field(None, description="Referenced department if identifiable")
    severity: str = Field(..., description="Low, Medium, High, Critical")
    resolution_status: str = Field(..., description="Open, Investigating, Escalated, Resolved")
    timestamp: str = Field(..., description="Feedback logged timestamp in ISO 8601")


# ============================================================================
# Data Quality & Validation Models
# ============================================================================

class ValidationIssue(BaseModel):
    """Data inconsistency or integrity issue."""
    category: str = Field(..., description="Data category where issue was found")
    record_id: Optional[str] = Field(None, description="Identifier of the faulty record")
    issue_type: str = Field(..., description="Missing Field, Invalid Reference, State Inconsistency, etc.")
    description: str = Field(..., description="Human-readable explanation of the integrity flaw")
    severity: str = Field(..., description="Warning or Error")


class DataQualityReport(BaseModel):
    """Overall data quality validation report."""
    hospital: str = "Sanjeevani Multispeciality Hospital"
    total_records_checked: int
    is_valid: bool
    issue_count: int
    issues: List[ValidationIssue]
    category_counts: Dict[str, int]


# ============================================================================
# Operational Intelligence & Bottleneck Models
# ============================================================================

class BottleneckIssue(BaseModel):
    """Identified hospital operational issue ranked by urgency and impact."""
    issue_id: str
    issue_type: str = Field(
        ...,
        description="LONG_WAITING_TIME, BED_SHORTAGE_OR_BLOCK, STAFF_WORKLOAD_IMBALANCE, "
                    "DELAYED_DIAGNOSTICS, STUCK_DISCHARGE, APPOINTMENT_ANOMALY, "
                    "OPERATIONAL_COMPLAINT, ESCALATION_REQUIRED"
    )
    title: str
    affected_department: str
    urgency: str = Field(..., description="Low, Medium, High, Critical")
    operational_impact: str = Field(..., description="Low, Medium, High, Critical")
    priority_score: int = Field(..., ge=0, le=100, description="0-100 calculated operational priority score")
    priority_level: str = Field(..., description="Critical, High, Medium, Low")
    evidence: List[str] = Field(default_factory=list, description="Direct supporting facts from records")
    possible_causes: List[str] = Field(default_factory=list, description="Plausible operational drivers")
    recommended_actions: List[str] = Field(default_factory=list, description="Suggested next operational steps")
    responsible_team: str = Field(..., description="Designated operational team")
    escalation_required: bool = False
    created_at: str = Field(..., description="Detection timestamp in ISO 8601")
    status: str = Field("Active", description="Active, Under Review, Mitigated, Resolved")
    details: Dict[str, Any] = Field(default_factory=dict, description="Structured supporting metrics")


class CausalLink(BaseModel):
    """Explainable cross-domain operational link between two issues or records."""
    link_id: str
    source_issue_id: str
    target_issue_id: str
    source_department: str
    target_department: str
    relationship_type: str = Field(
        ...,
        description="e.g. Bed_Block_Causes_ED_Wait, Diagnostic_Delay_Extends_Observation, Staff_Shortage_Hampers_Discharge"
    )
    supporting_evidence: List[str]
    explanation: str
    confidence: str = Field(..., description="High, Medium, Moderate")
    uncertainty_note: str


# ============================================================================
# Recommendations & Simulated Action Models
# ============================================================================

class Recommendation(BaseModel):
    """Actionable recommendation linked to a detected operational issue."""
    recommendation_id: str
    related_issue_id: str
    category: str = Field(
        ...,
        description="Discharge task prioritization, Diagnostic escalation, Staff shortage alert, "
                    "Staffing review or proposed reallocation, Appointment rescheduling recommendation, "
                    "Bed-management review, Department capacity review, Complaint escalation"
    )
    proposed_action: str
    reason: str
    supporting_evidence: List[str]
    responsible_team: str
    priority: str = Field(..., description="Critical, High, Medium, Low")
    review_status: str = Field("Pending", description="Pending, Action Created, Dismissed")


class ActionCreateRequest(BaseModel):
    """Payload to create a simulated action from a recommendation."""
    recommendation_id: str
    related_issue_id: str
    proposed_action: str
    responsible_team: str
    target_department: str
    priority: str = "Medium"
    notes: Optional[str] = None


class SimulatedAction(BaseModel):
    """Simulated task or alert queued for authorized demo operator review."""
    action_id: str
    recommendation_id: str
    related_issue_id: str
    action_type: str
    title: str
    description: str
    responsible_team: str
    target_department: str
    priority: str
    status: str = Field("Awaiting review", description="Awaiting review, Approved, Rejected, Completed")
    created_at: str
    updated_at: str
    created_by: str = "FlowCare AI Agent"
    reviewed_by: Optional[str] = None
    review_notes: Optional[str] = None
    completed_at: Optional[str] = None


class ActionReviewRequest(BaseModel):
    """Payload to approve or reject a simulated action."""
    status: str = Field(..., description="Approved or Rejected")
    reviewer_label: str = Field("Authorized Operator", description="Operator / Shift Manager label")
    notes: Optional[str] = Field(None, description="Review notes or approval condition")


class ActionCompleteRequest(BaseModel):
    """Payload to mark an approved simulated action as completed."""
    reviewer_label: str = Field("Authorized Operator", description="Operator / Staff label")
    notes: Optional[str] = Field(None, description="Completion summary notes")


class AuditLogEntry(BaseModel):
    """Historical audit entry recording status change of simulated tasks."""
    audit_id: str
    action_id: str
    previous_status: str
    new_status: str
    timestamp: str
    reviewer_label: str
    notes: Optional[str] = None


class DashboardSummary(BaseModel):
    """High-level operational health dashboard for the hospital."""
    hospital: str = "Sanjeevani Multispeciality Hospital"
    timestamp: str
    total_beds: int
    occupied_beds: int
    available_beds: int
    blocked_beds: int
    cleaning_beds: int
    occupancy_rate_pct: float
    overdue_diagnostics_count: int
    active_bottlenecks_count: int
    critical_issues_count: int
    pending_actions_count: int
    top_departments_needing_attention: List[str]
    priority_queue_summary: List[Dict[str, Any]]
