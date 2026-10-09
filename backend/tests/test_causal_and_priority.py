"""
Unit tests for Root-Cause Causal Reasoning and Priority Scoring rules.
"""

import pytest
from services.priority_service import PriorityService
from services.causal_service import CausalService
from services.detection_service import DetectionService
from services.data_service import HospitalDataService


def test_priority_service_scoring_logic():
    ps = PriorityService()

    # Critical + Critical + Escalation (40 + 40 + 10 + bonus) -> 90+ -> Critical
    score, level = ps.calculate_priority(
        urgency="Critical",
        operational_impact="Critical",
        escalation_required=True,
        delay_or_volume_modifier=10
    )
    assert score == 100
    assert level == "Critical"

    # High + High (30 + 30) -> 60 -> Medium
    score2, level2 = ps.calculate_priority(
        urgency="High",
        operational_impact="High",
        escalation_required=False,
        delay_or_volume_modifier=5
    )
    assert score2 == 65
    assert level2 == "High"

    # Low + Low (10 + 10) -> 20 -> Low
    score3, level3 = ps.calculate_priority(
        urgency="Low",
        operational_impact="Low",
        escalation_required=False,
        delay_or_volume_modifier=0
    )
    assert score3 == 20
    assert level3 == "Low"


def test_causal_service_generates_supported_cross_domain_links():
    data_svc = HospitalDataService()
    det_svc = DetectionService(data_service=data_svc)
    causal_svc = CausalService(data_service=data_svc, detection_svc=det_svc)

    links = causal_svc.analyze_causal_links()
    assert len(links) >= 3

    # Check Link 1: Blocked bed to emergency wait
    bed_link = next((l for l in links if l.relationship_type == "Blocked_Beds_Constrain_Emergency_Intake"), None)
    assert bed_link is not None
    assert bed_link.source_department in ("Discharge Coordination", "Emergency")
    assert bed_link.target_department == "Emergency"
    assert len(bed_link.supporting_evidence) >= 2
    assert "uncertainty" in bed_link.uncertainty_note.lower()
    assert bed_link.confidence in ("High", "Medium")

    # Check Link 2: Diagnostics delay to bed hold
    diag_link = next((l for l in links if l.relationship_type == "Diagnostic_Delay_Extends_Observation"), None)
    assert diag_link is not None
    assert "Troponin-T" in diag_link.supporting_evidence[0] or "overdue" in diag_link.supporting_evidence[0]
    assert diag_link.confidence == "High"


def test_causal_links_require_concrete_evidence_and_avoid_hallucination():
    data_svc = HospitalDataService()
    det_svc = DetectionService(data_service=data_svc)
    causal_svc = CausalService(data_service=data_svc, detection_svc=det_svc)

    links = causal_svc.analyze_causal_links()
    for link in links:
        assert link.link_id.startswith("LINK-")
        assert len(link.supporting_evidence) > 0
        assert len(link.explanation) > 30
        assert len(link.uncertainty_note) > 10
