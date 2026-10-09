"""
FlowCare AI — Comprehensive API Endpoint Status Code & Health Verifier
Sanjeevani Multispeciality Hospital
Cypher 2026 Hackathon — "The Blocked Bed"

This script tests every API route and verifies whether all expected endpoints
return HTTP 200 OK (and HTTP 201 Created for action creation).
"""

import sys
from fastapi.testclient import TestClient
from main import app


def run_verification():
    client = TestClient(app)
    print("=" * 80)
    print(" FlowCare AI — API Endpoint 200 OK Verification Suite")
    print(" Hospital: Sanjeevani Multispeciality Hospital")
    print("=" * 80)
    print(f"{'METHOD':<7} | {'ENDPOINT':<36} | {'STATUS':<6} | {'RESULT':<6} | DETAILS")
    print("-" * 80)

    results = []

    def check(method: str, path: str, expected_status: int = 200, json_body: dict = None):
        try:
            if method == "GET":
                resp = client.get(path)
            elif method == "POST":
                resp = client.post(path, json=json_body)
            elif method == "PATCH":
                resp = client.patch(path, json=json_body)
            else:
                resp = client.request(method, path, json=json_body)

            actual_status = resp.status_code
            is_ok = (actual_status == expected_status)
            result_str = "[PASS]" if is_ok else "[FAIL]"
            
            # Format preview details
            data = resp.json()
            if isinstance(data, list):
                details = f"{len(data)} items returned"
            elif isinstance(data, dict):
                if "status" in data:
                    details = f"status: {data['status']}"
                elif "is_valid" in data:
                    details = f"is_valid: {data['is_valid']}"
                elif "hospital" in data:
                    details = f"hospital: {data['hospital']}"
                elif "title" in data:
                    details = f"title: {data['title'][:30]}..."
                else:
                    details = f"{len(data)} keys"
            else:
                details = str(data)[:30]

            print(f"{method:<7} | {path:<36} | {actual_status:<6} | {result_str:<6} | {details}")
            results.append((method, path, expected_status, actual_status, is_ok))
            return resp
        except Exception as e:
            print(f"{method:<7} | {path:<36} | ERROR  | [FAIL] | Exception: {e}")
            results.append((method, path, expected_status, 500, False))
            return None

    # 1. Reset demo state first to guarantee clean baseline
    check("POST", "/demo/reset", expected_status=200)

    # 2. General Endpoints
    check("GET", "/health", expected_status=200)
    check("GET", "/", expected_status=200)

    # 3. Data & Validation Endpoints
    check("GET", "/data-quality", expected_status=200)
    check("GET", "/data/overview", expected_status=200)
    check("GET", "/data/patients", expected_status=200)
    check("GET", "/data/patients?department=Emergency", expected_status=200)
    check("GET", "/data/appointments", expected_status=200)
    check("GET", "/data/appointments?status=scheduled", expected_status=200)
    check("GET", "/data/beds", expected_status=200)
    check("GET", "/data/beds?ward=Emergency", expected_status=200)
    check("GET", "/data/staff", expected_status=200)
    check("GET", "/data/staff?shift=Morning", expected_status=200)
    check("GET", "/data/diagnostics", expected_status=200)
    check("GET", "/data/diagnostics?status=overdue", expected_status=200)
    check("GET", "/data/admissions", expected_status=200)
    check("GET", "/data/discharges", expected_status=200)
    check("GET", "/data/feedback", expected_status=200)
    check("GET", "/data/feedback?severity=High", expected_status=200)

    # 4. Operational Intelligence Endpoints
    check("GET", "/dashboard", expected_status=200)
    b_resp = check("GET", "/bottlenecks", expected_status=200)
    
    # Check detail for a valid issue ID
    first_issue_id = "ISSUE-BED-BLOCKED-DISCHARGE"
    if b_resp and b_resp.status_code == 200:
        issues = b_resp.json()
        if issues:
            first_issue_id = issues[0]["issue_id"]
    check("GET", f"/bottlenecks/{first_issue_id}", expected_status=200)

    check("GET", "/causal-links", expected_status=200)
    check("GET", "/recommendations", expected_status=200)
    check("GET", "/priority-queue", expected_status=200)

    # 5. Actions & Audit Lifecycle Endpoints
    check("GET", "/actions", expected_status=200)
    check("GET", "/actions?status=Awaiting%20review", expected_status=200)

    # Create a new action (expects 201 Created)
    create_resp = check("POST", "/actions", expected_status=201, json_body={
        "recommendation_id": "REC-001",
        "related_issue_id": "ISSUE-BED-BLOCKED-DISCHARGE",
        "proposed_action": "Coordinate with TPA desk for insurance clearance",
        "responsible_team": "Discharge Coordination",
        "target_department": "Emergency",
        "priority": "High"
    })

    if create_resp and create_resp.status_code == 201:
        new_act_id = create_resp.json()["action_id"]
        # Review action (Approve) -> expects 200 OK
        check("PATCH", f"/actions/{new_act_id}/review", expected_status=200, json_body={
            "status": "Approved",
            "reviewer_label": "Demo Operator Dr. Sharma",
            "notes": "Approved for simulation test"
        })
        # Complete action -> expects 200 OK
        check("PATCH", f"/actions/{new_act_id}/complete", expected_status=200, json_body={
            "reviewer_label": "Floor Supervisor",
            "notes": "Completed successfully"
        })

    check("GET", "/audit-log", expected_status=200)
    check("GET", f"/audit-log?action_id=ACT-001", expected_status=200)

    # Summary
    print("-" * 80)
    total_checks = len(results)
    passed_checks = sum(1 for _, _, _, _, is_ok in results if is_ok)
    failed_checks = total_checks - passed_checks

    print(f"TOTAL ENDPOINTS TESTED : {total_checks}")
    print(f"SUCCESSFUL CHECKS      : {passed_checks}")
    print(f"FAILED CHECKS          : {failed_checks}")
    print("=" * 80)

    if failed_checks == 0:
        print(">>> ALL ENDPOINTS RETURNED EXPECTED 200 / 201 STATUS CODES SUCCESSFULLY! <<<")
        return 0
    else:
        print(">>> WARNING: SOME ENDPOINTS FAILED TO RETURN EXPECTED STATUS CODES! <<<")
        return 1


if __name__ == "__main__":
    sys.exit(run_verification())
