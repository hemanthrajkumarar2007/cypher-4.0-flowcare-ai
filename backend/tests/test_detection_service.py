"""
Unit tests for all eight core problem-detection capabilities.
"""

import pytest
from services.data_service import HospitalDataService
from services.detection_service import DetectionService


def test_problem_1_long_waiting_times():
    svc = HospitalDataService()
    detector = DetectionService(data_service=svc)
    issues = detector.detect_long_waiting_times()

    assert len(issues) > 0
    em_issue = next((i for i in issues if i.affected_department == "Emergency"), None)
    assert em_issue is not None
    assert em_issue.issue_type == "LONG_WAITING_TIME"
    assert em_issue.urgency in ("Critical", "High")
    assert em_issue.priority_score >= 65
    assert len(em_issue.evidence) > 0
    assert "Triage" in em_issue.responsible_team


def test_problem_2_bed_shortages_idle_beds_blocked_beds():
    svc = HospitalDataService()
    detector = DetectionService(data_service=svc)
    issues = detector.detect_bed_bottlenecks()

    assert len(issues) >= 2
    # Verify blocked beds detection
    blocked_issue = next((i for i in issues if "BLOCKED" in i.issue_id), None)
    assert blocked_issue is not None
    assert "EMERG-03" in blocked_issue.evidence[0] or "EMERG-04" in blocked_issue.evidence[0]
    assert blocked_issue.priority_level == "Critical"

    # Verify ICU shortage detection
    icu_issue = next((i for i in issues if "ICU" in i.issue_id), None)
    assert icu_issue is not None
    assert icu_issue.details["occupancy_rate_pct"] == 100.0


def test_problem_3_staff_workload_imbalance():
    svc = HospitalDataService()
    detector = DetectionService(data_service=svc)
    issues = detector.detect_staff_workload_imbalance()

    assert len(issues) >= 1
    shortage_issue = next((i for i in issues if "SHORTAGE" in i.issue_id), None)
    assert shortage_issue is not None
    assert shortage_issue.affected_department == "Emergency"
    assert shortage_issue.details["shift"] == "Evening"
    assert shortage_issue.details["doctors_count"] <= 1


def test_problem_4_delayed_diagnostics():
    svc = HospitalDataService()
    detector = DetectionService(data_service=svc)
    issues = detector.detect_delayed_diagnostics()

    assert len(issues) > 0
    diag_issue = issues[0]
    assert diag_issue.issue_type == "DELAYED_DIAGNOSTICS"
    assert diag_issue.details["overdue_count"] >= 2
    assert diag_issue.details["max_delay_minutes"] >= 120
    assert any("Troponin-T" in ev for ev in diag_issue.evidence)


def test_problem_5_stuck_discharges():
    svc = HospitalDataService()
    detector = DetectionService(data_service=svc)
    issues = detector.detect_stuck_discharges()

    assert len(issues) == 1
    dis_issue = issues[0]
    assert dis_issue.issue_type == "STUCK_DISCHARGE"
    assert dis_issue.details["stuck_discharge_count"] == 2
    assert "EMERG-03" in dis_issue.details["linked_blocked_beds"]
    assert "EMERG-04" in dis_issue.details["linked_blocked_beds"]


def test_problem_6_appointment_anomalies():
    svc = HospitalDataService()
    detector = DetectionService(data_service=svc)
    issues = detector.detect_appointment_anomalies()

    assert len(issues) >= 2
    overload = next((i for i in issues if "OVERLOAD" in i.issue_id), None)
    assert overload is not None
    assert overload.affected_department == "Cardiology"
    assert overload.details["booking_count"] >= 4

    noshow = next((i for i in issues if "NOSHOW" in i.issue_id), None)
    assert noshow is not None
    assert noshow.affected_department == "Orthopedics"
    assert noshow.details["non_attendance_rate_pct"] == 100.0


def test_problem_7_operational_complaints():
    svc = HospitalDataService()
    detector = DetectionService(data_service=svc)
    issues = detector.detect_operational_complaints()

    assert len(issues) > 0
    comp_issue = issues[0]
    assert comp_issue.issue_type == "OPERATIONAL_COMPLAINT"
    assert comp_issue.details["complaint_count"] >= 1


def test_problem_8_escalations_and_all_detection_ranking():
    svc = HospitalDataService()
    detector = DetectionService(data_service=svc)
    all_issues = detector.detect_all_issues()

    assert len(all_issues) >= 8

    # Verify escalation issue present
    escalation = next((i for i in all_issues if i.issue_type == "ESCALATION_REQUIRED"), None)
    assert escalation is not None
    assert escalation.priority_level == "Critical"
    assert escalation.priority_score >= 85

    # Verify priority score descending ordering
    scores = [i.priority_score for i in all_issues]
    assert scores == sorted(scores, reverse=True)
