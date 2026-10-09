"""
Unit tests for Simulated Action Lifecycle, Review Workflow, and Audit Trail.
"""

import pytest
from services.action_service import ActionService
from models import ActionCreateRequest, ActionReviewRequest, ActionCompleteRequest


def test_action_service_seed_actions():
    svc = ActionService()
    actions = svc.get_actions()
    assert len(actions) >= 2
    assert all(a.status == "Awaiting review" for a in actions)

    audit = svc.get_audit_log()
    assert len(audit) >= 2
    assert all(e.new_status == "Awaiting review" for e in audit)


def test_create_action_lifecycle():
    svc = ActionService()
    req = ActionCreateRequest(
        recommendation_id="REC-001",
        related_issue_id="ISSUE-BED-BLOCKED-DISCHARGE",
        proposed_action="Test expedite paperwork",
        responsible_team="Discharge Unit",
        target_department="Emergency",
        priority="High"
    )
    action = svc.create_action(req)
    assert action.action_id.startswith("ACT-")
    assert action.status == "Awaiting review"

    # Verify audit log updated
    audit_entries = svc.get_audit_log(action_id=action.action_id)
    assert len(audit_entries) == 1
    assert audit_entries[0].new_status == "Awaiting review"


def test_action_review_workflow_approval_and_completion():
    svc = ActionService()
    act_id = "ACT-001"

    # Step 1: Review and Approve
    review_req = ActionReviewRequest(
        status="Approved",
        reviewer_label="Shift Medical Officer Dr. Sen",
        notes="Approved for immediate discharge liaison action."
    )
    reviewed = svc.review_action(act_id, review_req)
    assert reviewed.status == "Approved"
    assert reviewed.reviewed_by == "Shift Medical Officer Dr. Sen"

    # Step 2: Complete the Approved action
    comp_req = ActionCompleteRequest(
        reviewer_label="Discharge Liaison Staff",
        notes="Billing clearance obtained and summary signed."
    )
    completed = svc.complete_action(act_id, comp_req)
    assert completed.status == "Completed"
    assert completed.completed_at is not None

    # Step 3: Check audit trail sequence
    audit_entries = svc.get_audit_log(action_id=act_id)
    assert len(audit_entries) >= 3  # Initial creation -> Approved -> Completed
    statuses = [e.new_status for e in audit_entries]
    assert "Approved" in statuses
    assert "Completed" in statuses


def test_action_review_workflow_rejection():
    svc = ActionService()
    act_id = "ACT-002"

    review_req = ActionReviewRequest(
        status="Rejected",
        reviewer_label="Shift Administrator",
        notes="Rejected due to alternate laboratory priority."
    )
    reviewed = svc.review_action(act_id, review_req)
    assert reviewed.status == "Rejected"

    # Attempting to complete a rejected action must fail
    with pytest.raises(ValueError):
        svc.complete_action(act_id, ActionCompleteRequest(reviewer_label="Staff"))


def test_invalid_action_transitions():
    svc = ActionService()
    # Cannot review nonexistent action
    with pytest.raises(KeyError):
        svc.review_action("ACT-GHOST-999", ActionReviewRequest(status="Approved"))

    # Cannot complete an action that is still 'Awaiting review'
    with pytest.raises(ValueError):
        svc.complete_action("ACT-001", ActionCompleteRequest(reviewer_label="Staff"))
