"""
Dedicated test suite verifying the exact required benchmark scenario:
"At Sanjeevani Multispeciality Hospital, emergency waiting time has increased,
five beds are occupied, two beds are blocked by discharges awaiting paperwork,
several lab reports are late, and the next shift is short-staffed."
"""

import pytest
from services.data_service import HospitalDataService
from services.detection_service import DetectionService
from services.causal_service import CausalService
from services.recommendation_service import RecommendationService
from services.action_service import ActionService
from models import ActionReviewRequest, ActionCompleteRequest


def test_sanjeevani_core_challenge_scenario():
    # 1. Initialize data service
    data_svc = HospitalDataService()
    assert data_svc.hospital_name == "Sanjeevani Multispeciality Hospital"

    # 2. Verify Emergency Bed Occupancy: exactly 5 occupied beds, exactly 2 blocked by discharges
    em_beds = [b for b in data_svc.beds if "Emergency" in b.ward]
    assert len(em_beds) == 8

    occupied_em_beds = [b for b in em_beds if b.occupancy == "Occupied"]
    assert len(occupied_em_beds) == 5, "Emergency Ward must have exactly 5 occupied beds."

    blocked_em_beds = [b for b in occupied_em_beds if b.availability == "Blocked"]
    assert len(blocked_em_beds) == 2, "Exactly two beds must be blocked by discharges awaiting paperwork."

    active_inpatient_em_beds = [b for b in occupied_em_beds if b.availability == "Occupied"]
    assert len(active_inpatient_em_beds) == 3, "The other three occupied beds must be in active care, not blocked."

    blocked_bed_ids = {b.bed_id for b in blocked_em_beds}
    assert blocked_bed_ids == {"EMERG-03", "EMERG-04"}

    # 3. Verify Discharges awaiting paperwork
    discharges = data_svc.discharges
    assert len(discharges) == 2
    for d in discharges:
        assert d.document_status == "Incomplete"
        assert len(d.pending_tasks) > 0

    # 4. Verify Emergency Waiting Times Increased
    em_apts = [a for a in data_svc.appointments if a.department == "Emergency"]
    delayed_apts = [a for a in em_apts if a.waiting_time > 45]
    assert len(delayed_apts) >= 3
    avg_em_wait = sum(a.waiting_time for a in em_apts) / len(em_apts)
    assert avg_em_wait >= 70.0

    # 5. Verify Several Late Lab Reports
    overdue_tests = [d for d in data_svc.diagnostics if d.department == "Emergency" and d.status == "overdue"]
    assert len(overdue_tests) >= 3
    test_names = {t.test for t in overdue_tests}
    assert "Troponin-T" in test_names
    assert "Complete Blood Count (CBC)" in test_names
    assert "CT Scan Head" in test_names

    # 6. Verify Next Shift (Evening) Short-Staffed in Emergency
    em_evening_staff = [s for s in data_svc.staff if s.department == "Emergency" and s.shift == "Evening"]
    doctors = [s for s in em_evening_staff if s.role == "Doctor"]
    nurses = [s for s in em_evening_staff if s.role == "Nurse"]
    assert len(doctors) == 1
    assert len(nurses) == 1

    # 7. Run Detection Service and verify operational bottlenecks identified
    detector = DetectionService(data_service=data_svc)
    issues = detector.detect_all_issues()

    issue_types = {i.issue_type for i in issues}
    assert "LONG_WAITING_TIME" in issue_types
    assert "BED_SHORTAGE_OR_BLOCK" in issue_types
    assert "DELAYED_DIAGNOSTICS" in issue_types
    assert "STAFF_WORKLOAD_IMBALANCE" in issue_types
    assert "STUCK_DISCHARGE" in issue_types
    assert "ESCALATION_REQUIRED" in issue_types

    # 8. Verify Root-Cause Cross-Domain Causal Explanations
    causal_svc = CausalService(data_service=data_svc, detection_svc=detector)
    links = causal_svc.analyze_causal_links(issues)

    # Bed Block -> Emergency Wait
    bed_link = next((l for l in links if l.relationship_type == "Blocked_Beds_Constrain_Emergency_Intake"), None)
    assert bed_link is not None
    assert "EMERG-03" in bed_link.supporting_evidence[0]
    assert "EMERG-04" in bed_link.supporting_evidence[0]
    assert "triage" in bed_link.explanation.lower()

    # Diagnostic Delay -> Bed Hold
    diag_link = next((l for l in links if l.relationship_type == "Diagnostic_Delay_Extends_Observation"), None)
    assert diag_link is not None
    assert "Troponin-T" in diag_link.supporting_evidence[0] or "overdue" in diag_link.supporting_evidence[0]

    # Staff Shortage -> Handover Queue Risk
    staff_link = next((l for l in links if l.relationship_type == "Staff_Shortage_Amplifies_Queue_Congestion"), None)
    assert staff_link is not None

    # 9. Verify Actionable Recommendations
    rec_svc = RecommendationService(detection_svc=detector)
    recs = rec_svc.generate_recommendations(issues)

    rec_categories = {r.category for r in recs}
    assert "Discharge task prioritization" in rec_categories
    assert "Diagnostic escalation" in rec_categories
    assert "Staff shortage alert" in rec_categories

    # 10. Verify Simulated Action Workflow and Audit Trail
    act_svc = ActionService()
    actions = act_svc.get_actions()
    assert len(actions) >= 2

    # Operator approves discharge liaison task
    liaison_action = next((a for a in actions if "EMERG-03" in a.title or "Discharge" in a.title), None)
    assert liaison_action is not None
    assert liaison_action.status == "Awaiting review"

    reviewed = act_svc.review_action(
        liaison_action.action_id,
        ActionReviewRequest(status="Approved", reviewer_label="Shift In-Charge Dr. Ramesh", notes="Authorized immediate follow-up")
    )
    assert reviewed.status == "Approved"

    completed = act_svc.complete_action(
        liaison_action.action_id,
        ActionCompleteRequest(reviewer_label="Discharge Liaison Officer", notes="Paperwork cleared; bed moved to cleaning queue")
    )
    assert completed.status == "Completed"

    # Check audit log contains complete history
    audit = act_svc.get_audit_log(action_id=liaison_action.action_id)
    assert len(audit) == 3
    assert audit[0].new_status == "Awaiting review"
    assert audit[1].new_status == "Approved"
    assert audit[2].new_status == "Completed"
