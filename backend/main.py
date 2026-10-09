"""
FlowCare AI — Hospital Operations Intelligence & Bottleneck Resolution API
Hospital: Sanjeevani Multispeciality Hospital
Cypher 2026 Hackathon — "The Blocked Bed" Challenge
"""

from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware

from models import (
    Patient,
    Appointment,
    Bed,
    Staff,
    Diagnostic,
    Admission,
    Discharge,
    Feedback,
    DataQualityReport,
    BottleneckIssue,
    CausalLink,
    Recommendation,
    SimulatedAction,
    ActionCreateRequest,
    ActionReviewRequest,
    ActionCompleteRequest,
    AuditLogEntry,
    DashboardSummary,
)
from services.data_service import hospital_data_service
from services.detection_service import detection_service
from services.causal_service import causal_service
from services.recommendation_service import recommendation_service
from services.action_service import action_service


app = FastAPI(
    title="FlowCare AI — Hospital Operations Intelligence",
    description=(
        "Operational bottleneck detection, root-cause cross-domain reasoning, priority ranking, "
        "and simulated human-in-the-loop task review for Sanjeevani Multispeciality Hospital.\n\n"
        "**Hackathon Challenge:** Cypher 2026 — 'The Blocked Bed'\n\n"
        "**Clinical Safeguard Notice:** This system is an operational decision-support tool for demo purposes only. "
        "It does not perform clinical diagnosis, prescribe treatments, or execute automated real-world operational releases."
    ),
    version="1.0.0",
)

# Enable CORS for local testing / demo tools
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# General Endpoints
# ============================================================================

@app.get(
    "/health",
    tags=["General"],
    summary="Application Health Check",
    response_model=Dict[str, Any]
)
def health_check():
    """Returns application health and hospital configuration."""
    return {
        "status": "healthy",
        "service": "FlowCare AI Backend",
        "hospital": hospital_data_service.hospital_name,
        "version": "1.0.0",
        "reference_timestamp": hospital_data_service.reference_timestamp
    }


@app.get(
    "/",
    tags=["General"],
    summary="Service Information",
    response_model=Dict[str, Any]
)
def root():
    """Provides basic service information and feature overview."""
    return {
        "service": "FlowCare AI — Hospital Operations Intelligence",
        "hospital": hospital_data_service.hospital_name,
        "challenge": "Cypher 2026: The Blocked Bed",
        "documentation": "/docs",
        "openapi_schema": "/openapi.json",
        "capabilities": [
            "Synthetic Hospital Data Management (8 Categories)",
            "Data Quality & Relationship Validation Engine",
            "Eight Core Operational Problem Detections",
            "Cross-Domain Root-Cause Causal Reasoning",
            "Urgency & Operational Impact Priority Scoring",
            "Actionable Recommendations Engine",
            "Simulated Task & Alert Lifecycle Workflow",
            "Immutable Review Audit Trail"
        ],
        "disclaimer": "Fictional demonstration data only. No real clinical or operational hospital actions performed."
    }


# ============================================================================
# Data & Quality Endpoints
# ============================================================================

@app.get(
    "/data-quality",
    tags=["Data & Quality"],
    summary="Data Quality and Validation Report",
    response_model=DataQualityReport
)
def get_data_quality():
    """
    Evaluates dataset integrity, referential links, bed occupancy/availability consistency,
    and timestamp validity across all eight data categories.
    """
    return hospital_data_service.validate_data()


@app.get(
    "/data/overview",
    tags=["Data & Quality"],
    summary="Dataset Record Overview",
    response_model=Dict[str, Any]
)
def get_data_overview():
    """Returns record counts across all eight hospital data categories."""
    return hospital_data_service.get_overview()


@app.get(
    "/data/patients",
    tags=["Data & Quality"],
    summary="List Patient Records",
    response_model=List[Patient]
)
def get_patients(
    department: Optional[str] = Query(None, description="Filter by department"),
    status: Optional[str] = Query(None, description="Filter by status (Waiting, Admitted, etc.)"),
    age_group: Optional[str] = Query(None, description="Filter by age group"),
    visit_type: Optional[str] = Query(None, description="Filter by visit type (Emergency, Outpatient, etc.)")
):
    return hospital_data_service.get_patients(
        department=department,
        status=status,
        age_group=age_group,
        visit_type=visit_type
    )


@app.get(
    "/data/appointments",
    tags=["Data & Quality"],
    summary="List Appointment Records",
    response_model=List[Appointment]
)
def get_appointments(
    department: Optional[str] = Query(None, description="Filter by department"),
    doctor: Optional[str] = Query(None, description="Filter by attending doctor"),
    status: Optional[str] = Query(None, description="Filter by status (scheduled, completed, cancelled, no-show)")
):
    return hospital_data_service.get_appointments(
        department=department,
        doctor=doctor,
        status=status
    )


@app.get(
    "/data/beds",
    tags=["Data & Quality"],
    summary="List Hospital Beds",
    response_model=List[Bed]
)
def get_beds(
    ward: Optional[str] = Query(None, description="Filter by ward (Emergency Ward, ICU Ward, General Ward)"),
    bed_type: Optional[str] = Query(None, description="Filter by bed type (Emergency, ICU, General)"),
    occupancy: Optional[str] = Query(None, description="Filter by occupancy (Occupied, Unoccupied)"),
    availability: Optional[str] = Query(None, description="Filter by availability (Available, Occupied, Blocked, Cleaning)")
):
    return hospital_data_service.get_beds(
        ward=ward,
        bed_type=bed_type,
        occupancy=occupancy,
        availability=availability
    )


@app.get(
    "/data/staff",
    tags=["Data & Quality"],
    summary="List Hospital Staff",
    response_model=List[Staff]
)
def get_staff(
    department: Optional[str] = Query(None, description="Filter by department"),
    shift: Optional[str] = Query(None, description="Filter by shift (Morning, Evening, Night)"),
    availability: Optional[str] = Query(None, description="Filter by availability"),
    role: Optional[str] = Query(None, description="Filter by role (Doctor, Nurse, Technician)")
):
    return hospital_data_service.get_staff(
        department=department,
        shift=shift,
        availability=availability,
        role=role
    )


@app.get(
    "/data/diagnostics",
    tags=["Data & Quality"],
    summary="List Diagnostic Orders",
    response_model=List[Diagnostic]
)
def get_diagnostics(
    status: Optional[str] = Query(None, description="Filter by status (pending, in-progress, completed, overdue)"),
    department: Optional[str] = Query(None, description="Filter by ordering department"),
    patient: Optional[str] = Query(None, description="Filter by patient ID")
):
    return hospital_data_service.get_diagnostics(
        status=status,
        department=department,
        patient=patient
    )


@app.get(
    "/data/admissions",
    tags=["Data & Quality"],
    summary="List Inpatient Admissions",
    response_model=List[Admission]
)
def get_admissions(
    department: Optional[str] = Query(None, description="Filter by department"),
    ward: Optional[str] = Query(None, description="Filter by ward"),
    status: Optional[str] = Query(None, description="Filter by status (Active, Discharging, Discharged)")
):
    return hospital_data_service.get_admissions(
        department=department,
        ward=ward,
        status=status
    )


@app.get(
    "/data/discharges",
    tags=["Data & Quality"],
    summary="List Discharge Requests",
    response_model=List[Discharge]
)
def get_discharges(
    request_status: Optional[str] = Query(None, description="Filter by request status (Pending, Approved)"),
    document_status: Optional[str] = Query(None, description="Filter by document status (Incomplete, Cleared)")
):
    return hospital_data_service.get_discharges(
        request_status=request_status,
        document_status=document_status
    )


@app.get(
    "/data/feedback",
    tags=["Data & Quality"],
    summary="List Patient Feedback & Complaints",
    response_model=List[Feedback]
)
def get_feedback(
    category: Optional[str] = Query(None, description="Filter by category (Waiting Time, Bed Shortage, etc.)"),
    severity: Optional[str] = Query(None, description="Filter by severity (Low, Medium, High, Critical)"),
    department: Optional[str] = Query(None, description="Filter by department"),
    resolution_status: Optional[str] = Query(None, description="Filter by resolution status")
):
    return hospital_data_service.get_feedback(
        category=category,
        severity=severity,
        department=department,
        resolution_status=resolution_status
    )


# ============================================================================
# Operational Intelligence & Bottleneck Endpoints
# ============================================================================

@app.get(
    "/dashboard",
    tags=["Operational Intelligence"],
    summary="Operational Health Dashboard Summary",
    response_model=DashboardSummary
)
def get_dashboard():
    """Returns high-level KPI overview, bed utilization, bottleneck counts, and departments requiring focus."""
    beds = hospital_data_service.beds
    total_beds = len(beds)
    occupied_beds = sum(1 for b in beds if b.occupancy == "Occupied")
    available_beds = sum(1 for b in beds if b.availability == "Available")
    blocked_beds = sum(1 for b in beds if b.availability == "Blocked")
    cleaning_beds = sum(1 for b in beds if b.availability == "Cleaning")
    occ_rate = round((occupied_beds / total_beds) * 100, 1) if total_beds > 0 else 0.0

    issues = detection_service.detect_all_issues()
    critical_issues = sum(1 for i in issues if i.priority_level == "Critical")
    overdue_tests = sum(1 for d in hospital_data_service.diagnostics if d.status == "overdue")
    pending_actions = sum(1 for a in action_service.get_actions() if a.status == "Awaiting review")

    # Departments needing attention
    dept_counts = {}
    for i in issues:
        dept = i.affected_department
        dept_counts[dept] = dept_counts.get(dept, 0) + (2 if i.priority_level == "Critical" else 1)
    sorted_depts = sorted(dept_counts.keys(), key=lambda d: dept_counts[d], reverse=True)

    top_summary = [
        {
            "issue_id": i.issue_id,
            "title": i.title,
            "department": i.affected_department,
            "priority_level": i.priority_level,
            "priority_score": i.priority_score,
            "escalation_required": i.escalation_required
        }
        for i in issues[:5]
    ]

    return DashboardSummary(
        hospital=hospital_data_service.hospital_name,
        timestamp=hospital_data_service.reference_timestamp,
        total_beds=total_beds,
        occupied_beds=occupied_beds,
        available_beds=available_beds,
        blocked_beds=blocked_beds,
        cleaning_beds=cleaning_beds,
        occupancy_rate_pct=occ_rate,
        overdue_diagnostics_count=overdue_tests,
        active_bottlenecks_count=len(issues),
        critical_issues_count=critical_issues,
        pending_actions_count=pending_actions,
        top_departments_needing_attention=sorted_depts[:4],
        priority_queue_summary=top_summary
    )


@app.get(
    "/bottlenecks",
    tags=["Operational Intelligence"],
    summary="List Ranked Detected Bottlenecks",
    response_model=List[BottleneckIssue]
)
def get_bottlenecks():
    """Runs all 8 detection rules and returns detected operational issues ranked by priority score."""
    return detection_service.detect_all_issues()


@app.get(
    "/bottlenecks/{issue_id}",
    tags=["Operational Intelligence"],
    summary="Get Bottleneck Details and Evidence",
    response_model=BottleneckIssue
)
def get_bottleneck_by_id(issue_id: str):
    """Retrieves full details, evidence, possible causes, and actions for a specific issue ID."""
    issues = detection_service.detect_all_issues()
    for i in issues:
        if i.issue_id == issue_id:
            return i
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Bottleneck issue '{issue_id}' not found."
    )


@app.get(
    "/causal-links",
    tags=["Operational Intelligence"],
    summary="Explainable Cross-Domain Causal Links",
    response_model=List[CausalLink]
)
def get_causal_links():
    """
    Connects evidence across hospital datasets (waits, blocked beds, late diagnostics, staffing gaps)
    with transparent reasoning, evidence citations, confidence ratings, and documented uncertainties.
    """
    return causal_service.analyze_causal_links()


@app.get(
    "/recommendations",
    tags=["Operational Intelligence"],
    summary="Actionable Recommendations Linked to Issues",
    response_model=List[Recommendation]
)
def get_recommendations():
    """Generates prioritized, domain-specific recommendations for all active bottlenecks."""
    return recommendation_service.generate_recommendations()


@app.get(
    "/priority-queue",
    tags=["Operational Intelligence"],
    summary="Ranked Priority Queue of Actionable Issues",
    response_model=List[BottleneckIssue]
)
def get_priority_queue():
    """Returns all actionable issues sorted by priority score (most urgent and impactful first)."""
    return detection_service.detect_all_issues()


# ============================================================================
# Actions & Audit Endpoints
# ============================================================================

@app.get(
    "/actions",
    tags=["Actions & Audit"],
    summary="List Simulated Tasks and Alerts",
    response_model=List[SimulatedAction]
)
def get_actions(status: Optional[str] = Query(None, description="Filter by status (Awaiting review, Approved, Rejected, Completed)")):
    """Returns simulated actions queued for review or completed, optionally filtered by status."""
    return action_service.get_actions(status=status)


@app.post(
    "/actions",
    tags=["Actions & Audit"],
    summary="Create a Simulated Action from a Recommendation",
    response_model=SimulatedAction,
    status_code=status.HTTP_201_CREATED
)
def create_action(req: ActionCreateRequest):
    """
    Creates a new simulated action for staff review.
    Validates that referenced recommendation_id and related_issue_id exist.
    """
    # Validate issue existence
    all_issues = detection_service.detect_all_issues()
    issue_ids = {i.issue_id for i in all_issues}
    if req.related_issue_id not in issue_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Related issue '{req.related_issue_id}' does not exist."
        )

    # Validate recommendation existence
    all_recs = recommendation_service.generate_recommendations(all_issues)
    rec_ids = {r.recommendation_id for r in all_recs}
    if req.recommendation_id not in rec_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Recommendation '{req.recommendation_id}' does not exist."
        )

    return action_service.create_action(req)


@app.patch(
    "/actions/{action_id}/review",
    tags=["Actions & Audit"],
    summary="Review Simulated Action (Approve or Reject)",
    response_model=SimulatedAction
)
def review_action(action_id: str, review_req: ActionReviewRequest):
    """
    Approves or rejects a simulated action.
    Validates transition from 'Awaiting review' and logs status transition in audit log.
    Notice: Approving does NOT execute real clinical or operational changes.
    """
    try:
        return action_service.review_action(action_id, review_req)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Action '{action_id}' not found."
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.patch(
    "/actions/{action_id}/complete",
    tags=["Actions & Audit"],
    summary="Complete an Approved Simulated Action",
    response_model=SimulatedAction
)
def complete_action(action_id: str, comp_req: ActionCompleteRequest):
    """
    Marks an Approved simulated action as Completed.
    Validates transition and writes completion to audit log.
    """
    try:
        return action_service.complete_action(action_id, comp_req)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Action '{action_id}' not found."
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.get(
    "/audit-log",
    tags=["Actions & Audit"],
    summary="Historical Action Review Audit Log",
    response_model=List[AuditLogEntry]
)
def get_audit_log(action_id: Optional[str] = Query(None, description="Filter audit log by action ID")):
    """Returns immutable log of all simulated task transitions, reviewers, and timestamps."""
    return action_service.get_audit_log(action_id=action_id)


# ============================================================================
# Demo Utility Endpoint
# ============================================================================

@app.post(
    "/demo/reset",
    tags=["General"],
    summary="Reset Demo State",
    response_model=Dict[str, str]
)
def reset_demo():
    """Resets synthetic datasets and simulated actions back to initial benchmark scenario."""
    hospital_data_service.reset_to_default()
    action_service.seed_initial_actions()
    return {
        "status": "success",
        "message": "Demo data and simulated actions successfully reset to initial benchmark state for Sanjeevani Multispeciality Hospital."
    }
