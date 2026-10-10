"""
Integration tests for all FlowCare AI FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_and_root():
    r_health = client.get("/health")
    assert r_health.status_code == 200
    assert r_health.json()["status"] == "healthy"
    assert "Sanjeevani" in r_health.json()["hospital"]

    r_root = client.get("/")
    assert r_root.status_code == 200
    assert "capabilities" in r_root.json()


def test_data_quality_endpoint():
    r = client.get("/data-quality")
    assert r.status_code == 200
    data = r.json()
    assert data["is_valid"] is True
    assert data["total_records_checked"] > 30


def test_data_overview_and_entity_endpoints():
    r_overview = client.get("/data/overview")
    assert r_overview.status_code == 200
    assert r_overview.json()["counts"]["patients"] > 0

    # Patients
    r_pat = client.get("/data/patients?department=Emergency")
    assert r_pat.status_code == 200
    assert len(r_pat.json()) > 0
    assert all(p["department"] == "Emergency" for p in r_pat.json())

    # Appointments
    r_apt = client.get("/data/appointments?status=scheduled")
    assert r_apt.status_code == 200
    assert len(r_apt.json()) > 0

    # Beds
    r_beds = client.get("/data/beds?bed_type=Emergency")
    assert r_beds.status_code == 200
    assert len(r_beds.json()) >= 7

    # Staff
    r_staff = client.get("/data/staff?shift=Morning")
    assert r_staff.status_code == 200
    assert len(r_staff.json()) > 0

    # Diagnostics
    r_diag = client.get("/data/diagnostics?status=overdue")
    assert r_diag.status_code == 200
    assert len(r_diag.json()) >= 3

    # Admissions
    r_adm = client.get("/data/admissions?department=Emergency")
    assert r_adm.status_code == 200
    assert len(r_adm.json()) >= 4

    # Discharges
    r_dis = client.get("/data/discharges")
    assert r_dis.status_code == 200
    assert len(r_dis.json()) >= 2

    # Feedback
    r_fb = client.get("/data/feedback?severity=High")
    assert r_fb.status_code == 200
    assert len(r_fb.json()) >= 2


def test_dashboard_endpoint():
    r = client.get("/dashboard")
    assert r.status_code == 200
    d = r.json()
    assert d["total_beds"] > 0
    assert d["blocked_beds"] >= 2
    assert d["overdue_diagnostics_count"] >= 3
    assert len(d["top_departments_needing_attention"]) > 0
    assert "Emergency" in d["top_departments_needing_attention"]


def test_bottlenecks_and_issue_detail():
    r = client.get("/bottlenecks")
    assert r.status_code == 200
    issues = r.json()
    assert len(issues) >= 8

    # Fetch valid issue
    first_id = issues[0]["issue_id"]
    r_detail = client.get(f"/bottlenecks/{first_id}")
    assert r_detail.status_code == 200
    assert r_detail.json()["issue_id"] == first_id

    # Fetch invalid issue -> 404
    r_404 = client.get("/bottlenecks/NONEXISTENT-ISSUE-12345")
    assert r_404.status_code == 404


def test_causal_links_endpoint():
    r = client.get("/causal-links")
    assert r.status_code == 200
    links = r.json()
    assert len(links) >= 3
    assert any("Blocked" in l["relationship_type"] for l in links)


def test_recommendations_and_priority_queue():
    r_rec = client.get("/recommendations")
    assert r_rec.status_code == 200
    recs = r_rec.json()
    assert len(recs) >= 5

    r_queue = client.get("/priority-queue")
    assert r_queue.status_code == 200
    q = r_queue.json()
    assert len(q) >= 8


def test_actions_api_workflow():
    # 1. Reset demo state
    r_reset = client.post("/demo/reset")
    assert r_reset.status_code == 200

    # 2. Get initial actions
    r_actions = client.get("/actions")
    assert r_actions.status_code == 200
    assert len(r_actions.json()) >= 2

    # 3. Create simulated action with valid reference
    r_create = client.post("/actions", json={
        "recommendation_id": "REC-001",
        "related_issue_id": "ISSUE-BED-BLOCKED-DISCHARGE",
        "proposed_action": "Coordinate with TPA desk for insurance clearance",
        "responsible_team": "Discharge Coordination",
        "target_department": "Emergency",
        "priority": "High"
    })
    assert r_create.status_code == 201
    created_id = r_create.json()["action_id"]

    # 4. Create action with invalid recommendation -> 400
    r_bad = client.post("/actions", json={
        "recommendation_id": "REC-NONEXISTENT",
        "related_issue_id": "ISSUE-BED-BLOCKED-DISCHARGE",
        "proposed_action": "Invalid test",
        "responsible_team": "Test",
        "target_department": "Emergency",
        "priority": "High"
    })
    assert r_bad.status_code == 400

    # 5. Review action (Approve)
    r_rev = client.patch(f"/actions/{created_id}/review", json={
        "status": "Approved",
        "reviewer_label": "Demo Operator Dr. Sharma",
        "notes": "Approved for simulation test"
    })
    assert r_rev.status_code == 200
    assert r_rev.json()["status"] == "Approved"

    # 6. Complete action
    r_comp = client.patch(f"/actions/{created_id}/complete", json={
        "reviewer_label": "Floor Supervisor",
        "notes": "Completed successfully"
    })
    assert r_comp.status_code == 200
    assert r_comp.json()["status"] == "Completed"

    # 7. Check audit log
    r_audit = client.get(f"/audit-log?action_id={created_id}")
    assert r_audit.status_code == 200
    assert len(r_audit.json()) >= 3
