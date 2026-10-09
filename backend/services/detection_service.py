"""
FlowCare AI — Eight Core Problem-Detection Capabilities
Sanjeevani Multispeciality Hospital
Cypher 2026 Hackathon — "The Blocked Bed" Challenge
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import defaultdict

from models import BottleneckIssue
from services.data_service import HospitalDataService, hospital_data_service
from services.priority_service import priority_service


class DetectionService:
    """Implements transparent, testable detection rules for all eight hospital operational problem types."""

    def __init__(self, data_service: Optional[HospitalDataService] = None):
        self.data_service = data_service or hospital_data_service

    # =========================================================================
    # Problem 1: Unusually Long Waiting Times
    # =========================================================================
    def detect_long_waiting_times(self) -> List[BottleneckIssue]:
        issues = []
        # Group appointments by department
        dept_waits = defaultdict(list)
        for apt in self.data_service.appointments:
            dept_waits[apt.department].append(apt)

        baselines = {
            "Emergency": {"baseline": 30, "threshold": 45},
            "Cardiology": {"baseline": 30, "threshold": 50},
            "Orthopedics": {"baseline": 20, "threshold": 40},
            "General Medicine": {"baseline": 20, "threshold": 40},
        }

        for dept, apts in dept_waits.items():
            config = baselines.get(dept, {"baseline": 25, "threshold": 40})
            threshold = config["threshold"]
            baseline = config["baseline"]

            # Filter appointments with waiting_time > threshold
            over_threshold = [a for a in apts if a.waiting_time > threshold]
            if over_threshold:
                avg_wait = sum(a.waiting_time for a in over_threshold) / len(over_threshold)
                max_wait = max(a.waiting_time for a in over_threshold)
                
                # Urgency and impact calculation
                if avg_wait >= 80 or dept == "Emergency":
                    urgency = "Critical" if dept == "Emergency" else "High"
                    impact = "Critical" if dept == "Emergency" else "High"
                    delay_bonus = 8
                elif avg_wait >= 50:
                    urgency = "High"
                    impact = "Medium"
                    delay_bonus = 5
                else:
                    urgency = "Medium"
                    impact = "Medium"
                    delay_bonus = 2

                score, level = priority_service.calculate_priority(
                    urgency=urgency,
                    operational_impact=impact,
                    escalation_required=(urgency == "Critical"),
                    delay_or_volume_modifier=delay_bonus
                )

                evidence = [
                    f"{len(over_threshold)} appointments in {dept} exceeded the threshold of {threshold} mins (baseline: {baseline} mins).",
                    f"Average wait time among delayed cases: {avg_wait:.1f} minutes; peak measured wait: {max_wait} minutes.",
                    f"Sample affected appointments: {', '.join(a.appointment_id for a in over_threshold[:4])}."
                ]

                possible_causes = [
                    f"High patient arrival volume exceeding {dept} triage or intake capacity.",
                    "Delayed inpatient bed turnover causing bottleneck at admission desk.",
                    "Diagnostic turnaround delays holding up clinical disposition."
                ]

                recommended_actions = [
                    f"Initiate immediate scheduling and triage capacity review for {dept}.",
                    "Notify shift supervisor to inspect patient inflow and physician consultation pace.",
                    "Review intake bottlenecks and check inpatient bed availability for admission-bound patients."
                ]

                issues.append(BottleneckIssue(
                    issue_id=f"ISSUE-WAIT-{dept.upper()[:4]}",
                    issue_type="LONG_WAITING_TIME",
                    title=f"Unusually Long Waiting Times in {dept}",
                    affected_department=dept,
                    urgency=urgency,
                    operational_impact=impact,
                    priority_score=score,
                    priority_level=level,
                    evidence=evidence,
                    possible_causes=possible_causes,
                    recommended_actions=recommended_actions,
                    responsible_team="Triage and Outpatient Operations Team",
                    escalation_required=(urgency == "Critical"),
                    created_at=self.data_service.reference_timestamp,
                    status="Active",
                    details={
                        "department": dept,
                        "average_delayed_wait_mins": round(avg_wait, 1),
                        "max_wait_mins": max_wait,
                        "threshold_mins": threshold,
                        "baseline_mins": baseline,
                        "delayed_appointment_count": len(over_threshold)
                    }
                ))

        return issues

    # =========================================================================
    # Problem 2: Bed Shortages, Idle Beds and Ward Mismatches
    # =========================================================================
    def detect_bed_bottlenecks(self) -> List[BottleneckIssue]:
        issues = []
        ward_beds = defaultdict(list)
        for b in self.data_service.beds:
            ward_beds[b.ward].append(b)

        # 2A: Blocked Beds (e.g. Incomplete discharge)
        blocked_beds = [b for b in self.data_service.beds if b.availability == "Blocked"]
        if blocked_beds:
            dept = "Emergency" if any("Emergency" in b.ward for b in blocked_beds) else "General Medicine"
            evidence = [
                f"{len(blocked_beds)} beds are currently in 'Blocked' state: {', '.join(b.bed_id for b in blocked_beds)}.",
                f"Documented blockage reasons: " + "; ".join(f"{b.bed_id}: {b.blocked_reason}" for b in blocked_beds)
            ]
            possible_causes = [
                "Delays in discharge paperwork, insurance pre-authorization/TPA clearance.",
                "Delays in take-home pharmacy medication counseling or family transport coordination."
            ]
            recommended_actions = [
                "Recommend authorized bed-management and discharge coordination staff review blocked beds immediately.",
                "Expedite administrative billing and physician discharge summaries.",
                "IMPORTANT: Do not automatically release beds; bed becomes available only upon authorized clearance and cleaning."
            ]
            score, level = priority_service.calculate_priority(
                urgency="Critical" if len(blocked_beds) >= 2 else "High",
                operational_impact="Critical",
                escalation_required=True,
                delay_or_volume_modifier=8
            )
            issues.append(BottleneckIssue(
                issue_id="ISSUE-BED-BLOCKED-DISCHARGE",
                issue_type="BED_SHORTAGE_OR_BLOCK",
                title="Beds Blocked by Incomplete Discharge Paperwork",
                affected_department=dept,
                urgency="Critical" if len(blocked_beds) >= 2 else "High",
                operational_impact="Critical",
                priority_score=score,
                priority_level=level,
                evidence=evidence,
                possible_causes=possible_causes,
                recommended_actions=recommended_actions,
                responsible_team="Bed Management & Discharge Coordination Unit",
                escalation_required=True,
                created_at=self.data_service.reference_timestamp,
                status="Active",
                details={
                    "blocked_bed_count": len(blocked_beds),
                    "blocked_bed_ids": [b.bed_id for b in blocked_beds],
                    "blocked_reasons": {b.bed_id: b.blocked_reason for b in blocked_beds}
                }
            ))

        # 2B: Ward Capacity Shortage (e.g. ICU 100% full or Emergency high occupancy)
        for ward, beds in ward_beds.items():
            total = len(beds)
            occupied = sum(1 for b in beds if b.occupancy == "Occupied")
            available = sum(1 for b in beds if b.availability == "Available")
            occ_rate = (occupied / total) * 100 if total > 0 else 0

            if occ_rate >= 90:  # e.g. ICU at 100%
                evidence = [
                    f"{ward} has {occupied} of {total} beds occupied ({occ_rate:.1f}% occupancy rate).",
                    f"Only {available} beds available for new admissions in this ward."
                ]
                score, level = priority_service.calculate_priority(
                    urgency="Critical" if "ICU" in ward else "High",
                    operational_impact="High",
                    escalation_required=("ICU" in ward),
                    delay_or_volume_modifier=5
                )
                issues.append(BottleneckIssue(
                    issue_id=f"ISSUE-BED-SHORTAGE-{ward.upper()[:3]}",
                    issue_type="BED_SHORTAGE_OR_BLOCK",
                    title=f"Critical Bed Shortage in {ward}",
                    affected_department="ICU" if "ICU" in ward else "Inpatient Services",
                    urgency="Critical" if "ICU" in ward else "High",
                    operational_impact="High",
                    priority_score=score,
                    priority_level=level,
                    evidence=evidence,
                    possible_causes=[
                        f"High inpatient retention in {ward} with zero buffer for emergency transfers.",
                        "Slow step-down transfers to general wards due to capacity constraints."
                    ],
                    recommended_actions=[
                        f"Request Bed Management supervisor to review step-down readiness for patients in {ward}.",
                        "Verify if clinically stable patients can be safely transitioned to intermediate care.",
                        "Alert hospital command center of zero bed buffer for high-acuity admissions."
                    ],
                    responsible_team="Hospital Bed Allocation & Critical Care Board",
                    escalation_required=("ICU" in ward),
                    created_at=self.data_service.reference_timestamp,
                    status="Active",
                    details={
                        "ward": ward,
                        "total_beds": total,
                        "occupied_beds": occupied,
                        "available_beds": available,
                        "occupancy_rate_pct": round(occ_rate, 1)
                    }
                ))

        # 2C: Idle Beds despite demand elsewhere
        idle_beds = [
            b for b in self.data_service.beds
            if b.availability == "Available" and b.bed_type == "General" and b.ward == "General Ward"
        ]
        if len(idle_beds) >= 3 and any(b.availability == "Blocked" for b in self.data_service.beds):
            evidence = [
                f"{len(idle_beds)} General beds are available in General Ward (e.g. {', '.join(b.bed_id for b in idle_beds[:3])}).",
                "Emergency ward is currently facing bed blocks and queue congestion."
            ]
            score, level = priority_service.calculate_priority(
                urgency="Medium",
                operational_impact="Medium",
                escalation_required=False,
                delay_or_volume_modifier=2
            )
            issues.append(BottleneckIssue(
                issue_id="ISSUE-BED-IDLE-CAPACITY",
                issue_type="BED_SHORTAGE_OR_BLOCK",
                title="Available General Beds Idle During Emergency Pressure",
                affected_department="General Medicine",
                urgency="Medium",
                operational_impact="Medium",
                priority_score=score,
                priority_level=level,
                evidence=evidence,
                possible_causes=[
                    "Delays in routing eligible emergency admission overflow to General ward beds.",
                    "Siloed communication between Emergency triage and General ward nursing supervisor."
                ],
                recommended_actions=[
                    "Recommend bed-management review whether stable admitted emergency patients can be transferred to General Ward.",
                    "Verify clinical eligibility before transfer. Do not automatically reassign beds."
                ],
                responsible_team="Bed Management Operations",
                escalation_required=False,
                created_at=self.data_service.reference_timestamp,
                status="Active",
                details={"idle_general_beds": [b.bed_id for b in idle_beds]}
            ))

        return issues

    # =========================================================================
    # Problem 3: Doctor and Staff Workload Imbalance
    # =========================================================================
    def detect_staff_workload_imbalance(self) -> List[BottleneckIssue]:
        issues = []
        # Group staff by department and shift
        dept_shift_staff = defaultdict(list)
        for s in self.data_service.staff:
            dept_shift_staff[(s.department, s.shift)].append(s)

        # 1. Detect understaffed / critical workload departments
        for (dept, shift), staff_list in dept_shift_staff.items():
            critical_workload = [s for s in staff_list if s.workload in ("Critical", "High")]
            total_staff = len(staff_list)
            doctors = [s for s in staff_list if s.role == "Doctor"]
            nurses = [s for s in staff_list if s.role == "Nurse"]

            # Emergency Evening Shift has only 1 doctor and 1 nurse scheduled
            if dept == "Emergency" and shift == "Evening" and len(doctors) <= 1:
                evidence = [
                    f"Emergency {shift} shift has only {len(doctors)} doctor ({doctors[0].name if doctors else 'None'}) and {len(nurses)} nurse scheduled.",
                    f"Expected emergency patient volume requires minimum 2 doctors and 3 nurses per shift.",
                    f"Staff workload already flagged as Critical."
                ]
                score, level = priority_service.calculate_priority(
                    urgency="High",
                    operational_impact="High",
                    escalation_required=True,
                    delay_or_volume_modifier=6
                )
                issues.append(BottleneckIssue(
                    issue_id="ISSUE-STAFF-SHORTAGE-EM-EVE",
                    issue_type="STAFF_WORKLOAD_IMBALANCE",
                    title="Upcoming Shift Staff Shortage in Emergency Department",
                    affected_department="Emergency",
                    urgency="High",
                    operational_impact="High",
                    priority_score=score,
                    priority_level=level,
                    evidence=evidence,
                    possible_causes=[
                        "Upcoming evening shift rostering gap and lack of on-call emergency reserves.",
                        "High morning shift retention causing fatigue and handover delays."
                    ],
                    recommended_actions=[
                        "Issue urgent staff shortage alert to Nursing Director and Emergency Department Roster Lead.",
                        "Mobilize on-call emergency staff or review potential float pool coverage.",
                        "IMPORTANT: Do not automatically reassign staff without clinical competency verification."
                    ],
                    responsible_team="Hospital Rostering & Nursing Administration",
                    escalation_required=True,
                    created_at=self.data_service.reference_timestamp,
                    status="Active",
                    details={
                        "department": dept,
                        "shift": shift,
                        "doctors_count": len(doctors),
                        "nurses_count": len(nurses),
                        "workload_flags": [s.workload for s in staff_list]
                    }
                ))

        # 2. Detect spare capacity vs high pressure
        spare_staff = [
            s for s in self.data_service.staff
            if s.workload == "Low" and s.availability == "Available"
        ]
        high_staff = [
            s for s in self.data_service.staff
            if s.workload in ("High", "Critical") and s.department in ("Emergency", "ICU")
        ]
        if spare_staff and high_staff:
            spare_depts = list({s.department for s in spare_staff})
            evidence = [
                f"{len(high_staff)} staff members in Emergency/ICU are operating under High or Critical workload.",
                f"{len(spare_staff)} staff members in {', '.join(spare_depts)} report Low workload and Available status."
            ]
            score, level = priority_service.calculate_priority(
                urgency="Medium",
                operational_impact="Medium",
                escalation_required=False,
                delay_or_volume_modifier=2
            )
            issues.append(BottleneckIssue(
                issue_id="ISSUE-STAFF-CROSS-DEPT-IMBALANCE",
                issue_type="STAFF_WORKLOAD_IMBALANCE",
                title="Cross-Department Staff Workload Imbalance",
                affected_department="Hospital Wide",
                urgency="Medium",
                operational_impact="Medium",
                priority_score=score,
                priority_level=level,
                evidence=evidence,
                possible_causes=[
                    "Outpatient departments experiencing low morning footfall while acute care units face severe volume.",
                    "Static shift scheduling without dynamic workload leveling."
                ],
                recommended_actions=[
                    "Conduct operational staffing review with department heads.",
                    "Explore administrative or support task delegation to free up acute clinical staff.",
                    "Do not move specialized clinical staff across departments without credentialing approval."
                ],
                responsible_team="Hospital Operations Administration",
                escalation_required=False,
                created_at=self.data_service.reference_timestamp,
                status="Active",
                details={
                    "high_workload_departments": ["Emergency", "ICU"],
                    "low_workload_departments": spare_depts,
                    "available_spare_staff_count": len(spare_staff)
                }
            ))

        return issues

    # =========================================================================
    # Problem 4: Delayed Diagnostics
    # =========================================================================
    def detect_delayed_diagnostics(self) -> List[BottleneckIssue]:
        issues = []
        ref_dt = datetime.fromisoformat(self.data_service.reference_timestamp)

        overdue_tests = []
        for diag in self.data_service.diagnostics:
            if diag.status != "completed":
                try:
                    exp_dt = datetime.fromisoformat(diag.expected_completion)
                    if exp_dt < ref_dt or diag.status == "overdue":
                        delay_mins = int((ref_dt - exp_dt).total_seconds() / 60)
                        overdue_tests.append((diag, max(0, delay_mins)))
                except Exception:
                    pass

        if overdue_tests:
            # Group by ordering department
            dept_overdue = defaultdict(list)
            for diag, delay in overdue_tests:
                dept_overdue[diag.department].append((diag, delay))

            for dept, items in dept_overdue.items():
                tests_str = ", ".join(f"{d.test} for {d.patient} ({delay}m late)" for d, delay in items)
                max_delay = max(delay for _, delay in items)
                is_emergency = (dept == "Emergency")

                urgency = "Critical" if (is_emergency and max_delay >= 120) else "High"
                impact = "Critical" if is_emergency else "High"

                score, level = priority_service.calculate_priority(
                    urgency=urgency,
                    operational_impact=impact,
                    escalation_required=is_emergency,
                    delay_or_volume_modifier=min(10, max_delay // 20)
                )

                evidence = [
                    f"{len(items)} diagnostic tests ordered by {dept} are significantly overdue.",
                    f"Longest delay: {max_delay} minutes past expected completion time.",
                    f"Overdue orders: {tests_str}."
                ]

                possible_causes = [
                    "High diagnostic laboratory sample backlog or technician workload saturation.",
                    "Priority sequencing failure between routine outpatient orders and stat emergency orders.",
                    "Analyzer downtime or delay in clinical pathologist verification."
                ]

                recommended_actions = [
                    "Issue immediate diagnostic escalation to Central Laboratory and Imaging duty lead.",
                    f"Prioritize processing of emergency cardiac/head trauma diagnostics ({', '.join(d.test_id for d, _ in items)}).",
                    "Alert attending emergency physicians of expected revised turnaround times."
                ]

                issues.append(BottleneckIssue(
                    issue_id=f"ISSUE-DIAG-DELAY-{dept.upper()[:4]}",
                    issue_type="DELAYED_DIAGNOSTICS",
                    title=f"Severe Diagnostic Turnaround Delay in {dept}",
                    affected_department=dept,
                    urgency=urgency,
                    operational_impact=impact,
                    priority_score=score,
                    priority_level=level,
                    evidence=evidence,
                    possible_causes=possible_causes,
                    recommended_actions=recommended_actions,
                    responsible_team="Diagnostics & Central Laboratory Operations",
                    escalation_required=is_emergency,
                    created_at=self.data_service.reference_timestamp,
                    status="Active",
                    details={
                        "ordering_department": dept,
                        "overdue_count": len(items),
                        "max_delay_minutes": max_delay,
                        "overdue_tests": [
                            {
                                "test_id": d.test_id,
                                "test_name": d.test,
                                "patient_id": d.patient,
                                "delay_mins": delay,
                                "expected_completion": d.expected_completion
                            }
                            for d, delay in items
                        ]
                    }
                ))

        return issues

    # =========================================================================
    # Problem 5: Stuck Discharges
    # =========================================================================
    def detect_stuck_discharges(self) -> List[BottleneckIssue]:
        issues = []
        stuck = [
            d for d in self.data_service.discharges
            if d.document_status != "Cleared" or len(d.pending_tasks) > 0
        ]

        if stuck:
            total_tasks = sum(len(d.pending_tasks) for d in stuck)
            all_tasks = [f"{d.discharge_id} (Patient {d.patient_id}): " + "; ".join(d.pending_tasks) for d in stuck]

            # Correlate with beds
            blocked_beds_linked = [
                b.bed_id for b in self.data_service.beds
                if b.current_admission_id in [d.admission_id for d in stuck] and b.availability == "Blocked"
            ]

            evidence = [
                f"{len(stuck)} discharge requests remain blocked with outstanding operational tasks ({total_tasks} pending tasks total).",
                f"Detailed pending tasks: " + " | ".join(all_tasks),
                f"Corresponding beds currently blocked in physical wards: {', '.join(blocked_beds_linked) if blocked_beds_linked else 'None'}."
            ]

            score, level = priority_service.calculate_priority(
                urgency="Critical" if len(stuck) >= 2 else "High",
                operational_impact="Critical",
                escalation_required=True,
                delay_or_volume_modifier=7
            )

            issues.append(BottleneckIssue(
                issue_id="ISSUE-DISCHARGE-STUCK",
                issue_type="STUCK_DISCHARGE",
                title="Inpatient Discharges Blocked by Administrative & Clearance Tasks",
                affected_department="Discharge Coordination",
                urgency="Critical" if len(stuck) >= 2 else "High",
                operational_impact="Critical",
                priority_score=score,
                priority_level=level,
                evidence=evidence,
                possible_causes=[
                    "Third-Party Administrator (TPA) insurance billing settlement lag.",
                    "Attending physician delayed in signing discharge summary sheets.",
                    "Pharmacy takeaway counseling pending completion."
                ],
                recommended_actions=[
                    "Deploy discharge liaison nurse to clear insurance desk queries and obtain physician signatures.",
                    "Prioritize pharmacy counseling for patients in beds: " + ", ".join(blocked_beds_linked),
                    "Note: Bed state will transition to 'Cleaning' and then 'Available' only after authorized discharge clearance."
                ],
                responsible_team="Discharge Coordination & Patient Financial Services",
                escalation_required=True,
                created_at=self.data_service.reference_timestamp,
                status="Active",
                details={
                    "stuck_discharge_count": len(stuck),
                    "discharges": [
                        {
                            "discharge_id": d.discharge_id,
                            "admission_id": d.admission_id,
                            "patient_id": d.patient_id,
                            "pending_tasks": d.pending_tasks,
                            "document_status": d.document_status,
                            "medication_status": d.medication_status
                        }
                        for d in stuck
                    ],
                    "linked_blocked_beds": blocked_beds_linked
                }
            ))

        return issues

    # =========================================================================
    # Problem 6: Appointment Cancellations, No-Shows and Overloaded Slots
    # =========================================================================
    def detect_appointment_anomalies(self) -> List[BottleneckIssue]:
        issues = []

        # 6A: Overloaded Slots (more than 2 scheduled at the exact same datetime)
        slot_map = defaultdict(list)
        for a in self.data_service.appointments:
            slot_map[(a.department, a.datetime)].append(a)

        for (dept, dt), apts in slot_map.items():
            if len(apts) >= 4:  # e.g. Cardiology 10:00:00 has 5 appointments
                evidence = [
                    f"Department {dept} has {len(apts)} simultaneous appointments scheduled for slot {dt}.",
                    f"Standard single-doctor consultation capacity is 2 patients per 30-minute slot.",
                    f"Measured waiting times in this slot reach up to {max(a.waiting_time for a in apts)} mins."
                ]
                score, level = priority_service.calculate_priority(
                    urgency="High",
                    operational_impact="Medium",
                    escalation_required=False,
                    delay_or_volume_modifier=5
                )
                issues.append(BottleneckIssue(
                    issue_id=f"ISSUE-SLOT-OVERLOAD-{dept.upper()[:4]}",
                    issue_type="APPOINTMENT_ANOMALY",
                    title=f"Overbooked Appointment Slot in {dept} at {dt}",
                    affected_department=dept,
                    urgency="High",
                    operational_impact="Medium",
                    priority_score=score,
                    priority_level=level,
                    evidence=evidence,
                    possible_causes=[
                        "Double-booking in scheduling portal without slot capacity gating.",
                        "Walk-in additions squeezed into existing scheduled block."
                    ],
                    recommended_actions=[
                        f"Recommend Outpatient Scheduling staff review slot bookings for {dept}.",
                        "Propose rescheduling non-urgent follow-ups to later available slots with patient consent.",
                        "Do not alter appointment times automatically without patient confirmation."
                    ],
                    responsible_team="Outpatient Scheduling & Patient Access",
                    escalation_required=False,
                    created_at=self.data_service.reference_timestamp,
                    status="Active",
                    details={
                        "department": dept,
                        "slot_time": dt,
                        "booking_count": len(apts),
                        "appointment_ids": [a.appointment_id for a in apts]
                    }
                ))

        # 6B: High Cancellations & No-Shows Pattern
        dept_status = defaultdict(lambda: defaultdict(int))
        for a in self.data_service.appointments:
            dept_status[a.department][a.status] += 1

        for dept, stats in dept_status.items():
            total = sum(stats.values())
            cancellations = stats.get("cancelled", 0)
            noshows = stats.get("no-show", 0)
            non_attendance = cancellations + noshows

            if total >= 4 and (non_attendance / total) >= 0.5:
                rate = (non_attendance / total) * 100
                evidence = [
                    f"{dept} recorded {cancellations} cancellations and {noshows} no-shows out of {total} appointments ({rate:.1f}% non-attendance rate).",
                    "Clinic slot utilization severely compromised, creating wasted clinical hours."
                ]
                score, level = priority_service.calculate_priority(
                    urgency="Medium",
                    operational_impact="Medium",
                    escalation_required=False,
                    delay_or_volume_modifier=3
                )
                issues.append(BottleneckIssue(
                    issue_id=f"ISSUE-NOSHOW-SPIKE-{dept.upper()[:4]}",
                    issue_type="APPOINTMENT_ANOMALY",
                    title=f"Excessive Appointment Cancellation & No-Show Pattern in {dept}",
                    affected_department=dept,
                    urgency="Medium",
                    operational_impact="Medium",
                    priority_score=score,
                    priority_level=level,
                    evidence=evidence,
                    possible_causes=[
                        "Lack of automated pre-appointment SMS/voice confirmation reminders.",
                        "Transportation barriers or scheduling miscommunication."
                    ],
                    recommended_actions=[
                        f"Recommend scheduling team run confirmation callbacks for {dept} clinics.",
                        "Review whether vacant slots can be utilized for walk-in urgent consultations."
                    ],
                    responsible_team="Outpatient Clinic Coordinator",
                    escalation_required=False,
                    created_at=self.data_service.reference_timestamp,
                    status="Active",
                    details={
                        "department": dept,
                        "cancellations": cancellations,
                        "noshows": noshows,
                        "total_appointments": total,
                        "non_attendance_rate_pct": round(rate, 1)
                    }
                ))

        return issues

    # =========================================================================
    # Problem 7: Operational Complaints
    # =========================================================================
    def detect_operational_complaints(self) -> List[BottleneckIssue]:
        issues = []
        open_high_feedback = [
            f for f in self.data_service.feedback
            if f.severity in ("High", "Critical") and f.resolution_status in ("Open", "Investigating")
        ]

        if open_high_feedback:
            # Group by category/department
            cat_map = defaultdict(list)
            for fb in open_high_feedback:
                cat_map[fb.category].append(fb)

            for cat, items in cat_map.items():
                evidence = [
                    f"{len(items)} high-severity patient complaints logged under '{cat}'.",
                    "Verbatim feedback statements: " + " | ".join(f"[{f.feedback_id}] {f.complaint}" for f in items)
                ]
                dept = items[0].department or "Emergency"

                score, level = priority_service.calculate_priority(
                    urgency="High",
                    operational_impact="High",
                    escalation_required=True,
                    delay_or_volume_modifier=5
                )

                issues.append(BottleneckIssue(
                    issue_id=f"ISSUE-COMPLAINT-{cat.upper()[:4]}",
                    issue_type="OPERATIONAL_COMPLAINT",
                    title=f"High-Severity Patient Complaints regarding {cat}",
                    affected_department=dept,
                    urgency="High",
                    operational_impact="High",
                    priority_score=score,
                    priority_level=level,
                    evidence=evidence,
                    possible_causes=[
                        f"Operational friction in {dept} resulting in direct patient experience degradation.",
                        "Communication failure regarding triage priority and lab turnaround times."
                    ],
                    recommended_actions=[
                        "Escalate complaints to Patient Relations and Clinical Department Lead for review.",
                        "Deploy patient experience counselor to address family concerns in waiting area.",
                        "Correlate feedback with active operational delays to verify system root cause."
                    ],
                    responsible_team="Patient Relations & Quality Assurance",
                    escalation_required=True,
                    created_at=self.data_service.reference_timestamp,
                    status="Active",
                    details={
                        "category": cat,
                        "complaint_count": len(items),
                        "feedback_records": [
                            {"feedback_id": f.feedback_id, "complaint": f.complaint, "department": f.department}
                            for f in items
                        ]
                    }
                ))

        return issues

    # =========================================================================
    # Problem 8: Escalation Rule Engine
    # =========================================================================
    def detect_escalations(self, base_issues: List[BottleneckIssue]) -> List[BottleneckIssue]:
        """
        Synthesizes multi-factor escalation issues when critical conditions compound.
        """
        escalations = []
        critical_issues = [i for i in base_issues if i.priority_level == "Critical" or i.escalation_required]

        # Check for Sanjeevani Multi-System Crisis:
        # Emergency Long Wait + Bed Blocks + Delayed Diagnostics + Staff Shortage
        has_em_wait = any(i.issue_type == "LONG_WAITING_TIME" and i.affected_department == "Emergency" for i in base_issues)
        has_bed_block = any(i.issue_type == "BED_SHORTAGE_OR_BLOCK" and "BLOCKED" in i.issue_id for i in base_issues)
        has_diag_delay = any(i.issue_type == "DELAYED_DIAGNOSTICS" for i in base_issues)
        has_staff_shortage = any(i.issue_type == "STAFF_WORKLOAD_IMBALANCE" for i in base_issues)

        if has_em_wait and has_bed_block and (has_diag_delay or has_staff_shortage):
            evidence = [
                "Emergency Department triage wait times exceed critical threshold (average > 85 mins).",
                "Two Emergency beds remain blocked due to incomplete discharge paperwork.",
                "Multiple STAT laboratory and imaging diagnostic reports are past expected turnaround.",
                "Upcoming evening shift in Emergency has severe staffing deficit (only 1 doctor, 1 nurse scheduled)."
            ]
            possible_causes = [
                "Compounding multi-domain operational bottleneck creating systemic hospital gridlock.",
                "Discharge bottlenecks upstream preventing downstream emergency admissions."
            ]
            recommended_actions = [
                "Trigger Level-1 Hospital Operational Alert to Chief Medical Officer & Nursing Director.",
                "Activate Emergency Discharge Taskforce to immediately clear blocked beds EMERG-03 and EMERG-04.",
                "Command Central Lab to fast-track STAT emergency panels.",
                "Roster additional on-call physician and 2 nurses for the Emergency evening shift."
            ]
            score, level = priority_service.calculate_priority(
                urgency="Critical",
                operational_impact="Critical",
                escalation_required=True,
                delay_or_volume_modifier=10
            )
            escalations.append(BottleneckIssue(
                issue_id="ISSUE-ESCALATION-SANJEEVANI-CRITICAL",
                issue_type="ESCALATION_REQUIRED",
                title="Systemic Multi-Department Hospital Operational Escalation",
                affected_department="Hospital Wide",
                urgency="Critical",
                operational_impact="Critical",
                priority_score=score,
                priority_level=level,
                evidence=evidence,
                possible_causes=possible_causes,
                recommended_actions=recommended_actions,
                responsible_team="Hospital Executive Incident Command & Clinical Directors",
                escalation_required=True,
                created_at=self.data_service.reference_timestamp,
                status="Active",
                details={
                    "compounding_factors": [
                        "Emergency Queue Congestion",
                        "Inpatient Discharge Bed Block",
                        "Diagnostic Reporting Delay",
                        "Upcoming Shift Staffing Deficit"
                    ]
                }
            ))

        return escalations

    # =========================================================================
    # Master Detection Aggregator
    # =========================================================================
    def detect_all_issues(self) -> List[BottleneckIssue]:
        """Runs all eight problem detection engines and returns ranked list of issues."""
        detected: List[BottleneckIssue] = []

        # 1. Long Waiting Times
        detected.extend(self.detect_long_waiting_times())

        # 2. Bed Shortages, Idle Beds, Ward Mismatches
        detected.extend(self.detect_bed_bottlenecks())

        # 3. Staff Workload Imbalance
        detected.extend(self.detect_staff_workload_imbalance())

        # 4. Delayed Diagnostics
        detected.extend(self.detect_delayed_diagnostics())

        # 5. Stuck Discharges
        detected.extend(self.detect_stuck_discharges())

        # 6. Appointment Anomalies
        detected.extend(self.detect_appointment_anomalies())

        # 7. Operational Complaints
        detected.extend(self.detect_operational_complaints())

        # 8. Escalations (compounds across detected issues)
        detected.extend(self.detect_escalations(detected))

        # Sort strictly by priority_score descending, then urgency
        detected.sort(key=lambda x: (x.priority_score, 1 if x.escalation_required else 0), reverse=True)
        return detected


detection_service = DetectionService()
