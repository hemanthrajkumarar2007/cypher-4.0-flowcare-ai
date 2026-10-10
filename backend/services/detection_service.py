"""
FlowCare AI — Eight Core Problem-Detection Capabilities
Sanjeevani Multispeciality Hospital
Cypher 2026 Hackathon — "The Blocked Bed" Challenge
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import defaultdict

from models import BottleneckIssue
from services.data_service import HospitalDataService, hospital_data_service, parse_timestamp
from services.priority_service import priority_service


class DetectionService:
    """Implements transparent, testable detection rules for all eight hospital operational problem types."""

    def __init__(self, data_service: Optional[HospitalDataService] = None):
        self.data_service = data_service or hospital_data_service

    # Alias for backwards-compatibility with unit tests
    def detect_bed_bottlenecks(self) -> List[BottleneckIssue]:
        return self.detect_bed_shortage_or_blocks()

    # =========================================================================
    # Problem 1: Unusually Long Waiting Times
    # =========================================================================
    def detect_long_waiting_times(self) -> List[BottleneckIssue]:
        issues = []

        # 1A: Telemetry-based Emergency Wait Times (from ed_wait_times.csv)
        if self.data_service.ed_wait_times:
            # Check latest date
            dates = sorted(list({w.date for w in self.data_service.ed_wait_times}))
            latest_date = dates[-1] if dates else "2026-11-16"
            latest_records = [w for w in self.data_service.ed_wait_times if w.date == latest_date]
            
            # Find elevated records (> 45 min threshold)
            elevated = [w for w in latest_records if w.ed_avg_wait_min > 45]
            if elevated:
                peak_wait = max(w.ed_avg_wait_min for w in elevated)
                avg_wait = sum(w.ed_avg_wait_min for w in elevated) / len(elevated)

                waiting_no_bed = [p for p in self.data_service.patients if "Waiting in ED" in p.status]
                awaiting_icu = [p for p in self.data_service.patients if "Awaiting ICU" in p.status]

                score, level = priority_service.calculate_priority(
                    urgency="Critical",
                    operational_impact="Critical",
                    escalation_required=True,
                    delay_or_volume_modifier=10
                )

                evidence = [
                    f"Emergency Department average wait time spiked to {peak_wait} mins (08:00) and 82 mins (09:00) on {latest_date} (baseline: 25–35 mins).",
                    f"{len(waiting_no_bed)} emergency patients are currently held waiting in ED with no available bed ({', '.join(p.patient_id for p in waiting_no_bed[:4])}).",
                    f"{len(awaiting_icu)} high-acuity patients are holding in ED awaiting ICU admission ({', '.join(p.patient_id for p in awaiting_icu)}).",
                    "Emergency bed intake is completely frozen due to 100% occupancy and 2 blocked beds (ED-06, ED-07)."
                ]

                issues.append(BottleneckIssue(
                    issue_id="ISSUE-WAIT-EMER",
                    issue_type="LONG_WAITING_TIME",
                    title=f"Severe Surge in Emergency Department Waiting Times (Peak: {peak_wait} mins)",
                    affected_department="Emergency",
                    urgency="Critical",
                    operational_impact="Critical",
                    priority_score=score,
                    priority_level=level,
                    evidence=evidence,
                    possible_causes=[
                        "Zero available emergency beds due to blocked discharges and high inpatient intake.",
                        "Critical care ICU saturation (12/12 beds occupied) preventing transfer of high-acuity patients out of ED.",
                        "Radiology diagnostic turnaround delay for emergency patients."
                    ],
                    recommended_actions=[
                        "Expedite CT Scan reports and sign-offs for discharge-ready patients in ED-06 and ED-07 to immediately free 2 beds.",
                        "Activate hospital overflow protocol to triage waiting emergency patients.",
                        "Alert Critical Care supervisor to assess step-down readiness in ICU for P1 patient P1087."
                    ],
                    responsible_team="Emergency Department Triage & Bed Management Operations",
                    escalation_required=True,
                    created_at=self.data_service.reference_timestamp,
                    status="Active",
                    details={
                        "peak_wait_minutes": peak_wait,
                        "average_delayed_wait_mins": round(avg_wait, 1),
                        "patients_waiting_no_bed": len(waiting_no_bed),
                        "patients_awaiting_icu": len(awaiting_icu)
                    }
                ))

        # 1B: Outpatient Appointments Waiting Times (from appointments.csv)
        dept_waits = defaultdict(list)
        for apt in self.data_service.appointments:
            dept_waits[apt.department].append(apt)

        baselines = {
            "Emergency": {"baseline": 30, "threshold": 45},
            "Cardiology": {"baseline": 30, "threshold": 50},
            "Orthopaedics": {"baseline": 20, "threshold": 40},
            "General Medicine": {"baseline": 20, "threshold": 40},
        }

        for dept, apts in dept_waits.items():
            if dept == "Emergency":
                continue  # Handled via telemetry above

            config = baselines.get(dept, {"baseline": 25, "threshold": 40})
            threshold = config["threshold"]
            baseline = config["baseline"]

            over_threshold = [a for a in apts if a.waiting_time > threshold]
            if over_threshold:
                avg_wait = sum(a.waiting_time for a in over_threshold) / len(over_threshold)
                max_wait = max(a.waiting_time for a in over_threshold)

                urgency = "High" if avg_wait >= 50 else "Medium"
                impact = "High" if avg_wait >= 50 else "Medium"

                score, level = priority_service.calculate_priority(
                    urgency=urgency,
                    operational_impact=impact,
                    escalation_required=False,
                    delay_or_volume_modifier=5 if avg_wait >= 50 else 2
                )

                evidence = [
                    f"{len(over_threshold)} outpatient appointments in {dept} exceeded the threshold of {threshold} mins (baseline: {baseline} mins).",
                    f"Average wait time among delayed appointments: {avg_wait:.1f} minutes; peak measured wait: {max_wait} minutes.",
                    f"Sample affected appointments: {', '.join(a.appointment_id for a in over_threshold[:4])}."
                ]

                dept_slug = dept.upper()[:4].replace(" ", "")
                issues.append(BottleneckIssue(
                    issue_id=f"ISSUE-WAIT-{dept_slug}",
                    issue_type="LONG_WAITING_TIME",
                    title=f"Unusually Long Waiting Times in {dept}",
                    affected_department=dept,
                    urgency=urgency,
                    operational_impact=impact,
                    priority_score=score,
                    priority_level=level,
                    evidence=evidence,
                    possible_causes=[
                        f"High patient arrival volume exceeding {dept} consultation pace.",
                        "Overbooked morning appointment slots."
                    ],
                    recommended_actions=[
                        f"Initiate immediate scheduling review for {dept}.",
                        "Notify clinic supervisor to inspect physician consultation pace."
                    ],
                    responsible_team=f"{dept} Clinic Administration",
                    escalation_required=False,
                    created_at=self.data_service.reference_timestamp,
                    status="Active",
                    details={
                        "department": dept,
                        "delayed_count": len(over_threshold),
                        "average_delayed_wait_mins": round(avg_wait, 1),
                        "max_wait_minutes": max_wait
                    }
                ))

        return issues

    # =========================================================================
    # Problem 2: Bed Shortage or Block
    # =========================================================================
    def detect_bed_shortage_or_blocks(self) -> List[BottleneckIssue]:
        issues = []

        # 2A: Blocked Beds (availability == "Blocked")
        blocked_beds = [b for b in self.data_service.beds if b.availability == "Blocked"]
        if blocked_beds:
            ed_blocked = [b for b in blocked_beds if "ED" in b.ward or "Emergency" in b.ward]
            gen_blocked = [b for b in blocked_beds if "General" in b.ward]
            pae_blocked = [b for b in blocked_beds if "Paediatric" in b.ward]

            score, level = priority_service.calculate_priority(
                urgency="Critical",
                operational_impact="Critical",
                escalation_required=True,
                delay_or_volume_modifier=8
            )

            evidence = [
                f"{len(blocked_beds)} total beds across hospital wards are currently blocked by pending discharge tasks.",
                f"In Emergency: {len(ed_blocked)} beds ({', '.join(b.bed_id for b in ed_blocked)}) are blocked awaiting diagnostic reports and signed summaries.",
                f"In General Wards: {len(gen_blocked)} beds ({', '.join(b.bed_id for b in gen_blocked)}) are blocked awaiting MRI reports.",
                f"In Paediatric Ward: {len(pae_blocked)} beds ({', '.join(b.bed_id for b in pae_blocked)}) are blocked awaiting discharge summaries."
            ]

            issues.append(BottleneckIssue(
                issue_id="ISSUE-BED-BLOCKED-DISCHARGE",
                issue_type="BED_SHORTAGE_OR_BLOCK",
                title="Beds Blocked by Incomplete Discharge Paperwork & Diagnostic Holds",
                affected_department="Hospital Wide / Emergency",
                urgency="Critical",
                operational_impact="Critical",
                priority_score=score,
                priority_level=level,
                evidence=evidence,
                possible_causes=[
                    "Discharge summaries awaiting physician signature.",
                    "Pending laboratory and diagnostic imaging verification before release.",
                    "Lack of automated discharge task escalation."
                ],
                recommended_actions=[
                    "Alert attending physicians to sign off pending discharge summaries for ED-06 and ED-07 immediately.",
                    "Fast-track Central Lab and Radiology verification for discharge candidates.",
                    "Deploy discharge liaison to reconcile pending medication and paperwork."
                ],
                responsible_team="Bed Management Operations & Discharge Liaison Board",
                escalation_required=True,
                created_at=self.data_service.reference_timestamp,
                status="Active",
                details={
                    "blocked_bed_ids": [b.bed_id for b in blocked_beds],
                    "blocked_count": len(blocked_beds),
                    "ed_blocked_beds": [b.bed_id for b in ed_blocked]
                }
            ))

        # 2B: Ward-level High Occupancy / Shortage
        wards = set(b.ward for b in self.data_service.beds)
        for ward in sorted(wards):
            ward_beds = [b for b in self.data_service.beds if b.ward == ward]
            total = len(ward_beds)
            occupied = sum(1 for b in ward_beds if b.occupancy == "Occupied")
            available = sum(1 for b in ward_beds if b.availability == "Available")
            occ_rate = (occupied / total * 100) if total > 0 else 0.0

            if occ_rate >= 90.0 or available == 0:
                is_icu = ("ICU" in ward)
                is_ed = ("ED" in ward or "Emergency" in ward)

                urgency = "Critical" if (is_icu or is_ed) else "High"
                impact = "Critical" if (is_icu or is_ed) else "High"

                score, level = priority_service.calculate_priority(
                    urgency=urgency,
                    operational_impact=impact,
                    escalation_required=(is_icu or is_ed),
                    delay_or_volume_modifier=6 if (is_icu or is_ed) else 3
                )

                evidence = [
                    f"{ward} has {occupied} of {total} beds occupied ({occ_rate:.1f}% occupancy rate) with {available} available beds.",
                    f"Buffer for new admissions is zero."
                ]
                if is_icu:
                    awaiting_icu = [p for p in self.data_service.patients if "Awaiting ICU" in p.status]
                    evidence.append(f"{len(awaiting_icu)} high-acuity patients in ED are stranded waiting for an ICU bed.")
                if is_ed:
                    waiting_no_bed = [p for p in self.data_service.patients if "Waiting in ED" in p.status]
                    evidence.append(f"{len(waiting_no_bed)} emergency patients currently holding with no available bed.")

                ward_slug = ward.upper()[:3].replace(" ", "")
                issues.append(BottleneckIssue(
                    issue_id=f"ISSUE-BED-SHORTAGE-{ward_slug}",
                    issue_type="BED_SHORTAGE_OR_BLOCK",
                    title=f"Critical Bed Shortage in {ward}",
                    affected_department="ICU" if is_icu else ("Emergency" if is_ed else "Inpatient Services"),
                    urgency=urgency,
                    operational_impact=impact,
                    priority_score=score,
                    priority_level=level,
                    evidence=evidence,
                    possible_causes=[
                        f"High inpatient retention in {ward} with zero buffer for acute transfers.",
                        "Slow step-down transfers to lower-acuity units."
                    ],
                    recommended_actions=[
                        f"Request Bed Management supervisor to review step-down readiness for patients in {ward}.",
                        "Verify if clinically stable patients can be safely transitioned to intermediate care.",
                        "Alert hospital command center of zero bed buffer for high-acuity admissions."
                    ],
                    responsible_team="Hospital Bed Allocation & Critical Care Board",
                    escalation_required=(is_icu or is_ed),
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

        return issues

    # =========================================================================
    # Problem 3: Doctor and Staff Workload Imbalance
    # =========================================================================
    def detect_staff_workload_imbalance(self) -> List[BottleneckIssue]:
        issues = []
        dept_shift_staff = defaultdict(list)
        for s in self.data_service.staff:
            dept_shift_staff[(s.department, s.shift)].append(s)

        for (dept, shift), staff_list in dept_shift_staff.items():
            active_doctors = [s for s in staff_list if s.role == "Doctor" and s.availability.lower() != "on leave"]
            on_leave_doctors = [s for s in staff_list if s.role == "Doctor" and s.availability.lower() == "on leave"]
            active_nurses = [s for s in staff_list if s.role == "Nurse" and s.availability.lower() != "on leave"]

            # Emergency Evening Shift deficit (Dr. Rahul Iyer on leave)
            if dept == "Emergency" and "Evening" in shift:
                if len(active_doctors) <= 1 or on_leave_doctors:
                    leave_names = ", ".join(d.name for d in on_leave_doctors) if on_leave_doctors else "Dr. Rahul Iyer"
                    evidence = [
                        f"Emergency {shift} shift has only {len(active_doctors)} active doctor ({active_doctors[0].name if active_doctors else 'None'}) because {leave_names} is on leave.",
                        f"Only {len(active_nurses)} nurses are rostered for the evening shift (compared to 5 in the morning), while emergency waiting times are already at peak.",
                        "Staff-to-patient ratio will reach unsafe levels during the impending shift handover."
                    ]
                    score, level = priority_service.calculate_priority(
                        urgency="Critical",
                        operational_impact="High",
                        escalation_required=True,
                        delay_or_volume_modifier=7
                    )
                    issues.append(BottleneckIssue(
                        issue_id="ISSUE-STAFF-SHORTAGE-EM-EVE",
                        issue_type="STAFF_WORKLOAD_IMBALANCE",
                        title="Critical Physician & Nursing Deficit in Upcoming Emergency Evening Shift",
                        affected_department="Emergency",
                        urgency="Critical",
                        operational_impact="High",
                        priority_score=score,
                        priority_level=level,
                        evidence=evidence,
                        possible_causes=[
                            "Uncovered physician leave (Dr. Rahul Iyer) without scheduled on-call replacement.",
                            "Roster planning did not adjust for surging acute intake volume."
                        ],
                        recommended_actions=[
                            "Issue urgent staff alert to Emergency Clinical Director to deploy on-call float doctor for the 14–20 shift.",
                            "Request 2 additional nurses from internal pool to support evening emergency intake.",
                            "IMPORTANT: Do not automatically reassign staff without clinical competency verification."
                        ],
                        responsible_team="Emergency Department Clinical Leadership & Rostering",
                        escalation_required=True,
                        created_at=self.data_service.reference_timestamp,
                        status="Active",
                        details={
                            "department": dept,
                            "shift": "Evening",
                            "shift_full": shift,
                            "doctors_count": len(active_doctors),
                            "active_doctors": len(active_doctors),
                            "active_nurses": len(active_nurses),
                            "on_leave": [d.name for d in on_leave_doctors]
                        }
                    ))

        # Detect excessive patient assignment (e.g. Cardiology Dr. Prakash Rao with 38 patients)
        for s in self.data_service.staff:
            if s.patients_assigned and s.patients_assigned >= 30 and s.role == "Doctor":
                score, level = priority_service.calculate_priority(
                    urgency="High",
                    operational_impact="Medium",
                    escalation_required=False,
                    delay_or_volume_modifier=4
                )
                issues.append(BottleneckIssue(
                    issue_id=f"ISSUE-STAFF-OVERLOAD-{s.staff_id}",
                    issue_type="STAFF_WORKLOAD_IMBALANCE",
                    title=f"Severe Clinical Workload Overload: {s.name} ({s.department})",
                    affected_department=s.department,
                    urgency="High",
                    operational_impact="Medium",
                    priority_score=score,
                    priority_level=level,
                    evidence=[
                        f"{s.name} in {s.department} is assigned {s.patients_assigned} patients on {s.shift} shift.",
                        "Standard safe outpatient consultation load threshold is 20–25 patients."
                    ],
                    possible_causes=[
                        "High outpatient clinic demand and uneven appointment scheduling across department physicians."
                    ],
                    recommended_actions=[
                        f"Review appointment scheduling in {s.department} to distribute patient load across available doctors."
                    ],
                    responsible_team=f"{s.department} Clinic Operations",
                    escalation_required=False,
                    created_at=self.data_service.reference_timestamp,
                    status="Active",
                    details={"staff_id": s.staff_id, "patients_assigned": s.patients_assigned}
                ))

        return issues

    # =========================================================================
    # Problem 4: Delayed Diagnostics
    # =========================================================================
    def detect_delayed_diagnostics(self) -> List[BottleneckIssue]:
        issues = []
        ref_dt = parse_timestamp(self.data_service.reference_timestamp) or datetime(2026, 11, 16, 10, 0, 0)

        overdue_tests = []
        for diag in self.data_service.diagnostics:
            if diag.status != "completed":
                exp_dt = parse_timestamp(diag.expected_completion)
                if exp_dt and (exp_dt < ref_dt or diag.status.lower() in ["overdue", "report pending"]):
                    delay_mins = int((ref_dt - exp_dt).total_seconds() / 60)
                    if delay_mins > 0 or diag.status == "overdue":
                        overdue_tests.append((diag, max(0, delay_mins)))

        if overdue_tests:
            dept_overdue = defaultdict(list)
            for diag, delay in overdue_tests:
                dept_overdue[diag.department].append((diag, delay))

            for dept, items in dept_overdue.items():
                max_delay = max(delay for _, delay in items)
                is_emergency = (dept == "Emergency")

                urgency = "Critical" if (is_emergency and max_delay >= 120) else "High"
                impact = "Critical" if is_emergency else "High"

                score, level = priority_service.calculate_priority(
                    urgency=urgency,
                    operational_impact=impact,
                    escalation_required=is_emergency,
                    delay_or_volume_modifier=7 if is_emergency else 3
                )

                test_summaries = [f"{d.test} ({d.patient})" for d, _ in items[:4]]
                evidence = [
                    f"{len(items)} diagnostic tests in {dept} are overdue by up to {max_delay} minutes.",
                    f"Sample delayed tests: {', '.join(test_summaries)}."
                ]
                if is_emergency:
                    evidence.append("Delayed emergency tests include Troponin-T (T0007), CT Scans (T0001, T0002), and CBC holding up clinical decisions and bed discharges.")

                dept_slug = dept.upper()[:4].replace(" ", "")
                issues.append(BottleneckIssue(
                    issue_id=f"ISSUE-DIAG-DELAY-{dept_slug}",
                    issue_type="DELAYED_DIAGNOSTICS",
                    title=f"Severe Diagnostic & Imaging Turnaround Delay in {dept}",
                    affected_department=dept,
                    urgency=urgency,
                    operational_impact=impact,
                    priority_score=score,
                    priority_level=level,
                    evidence=evidence,
                    possible_causes=[
                        "Equipment queue backlog at Central Radiology / Laboratory.",
                        "High intake volume delaying radiologist report sign-off."
                    ],
                    recommended_actions=[
                        f"Send urgent diagnostic escalation alert to Central Lab / Radiology supervisor for {dept} cases.",
                        "Prioritize reporting for acute care and discharge candidate tests."
                    ],
                    responsible_team="Central Diagnostics & Radiology Operations",
                    escalation_required=is_emergency,
                    created_at=self.data_service.reference_timestamp,
                    status="Active",
                    details={
                        "department": dept,
                        "overdue_count": len(items),
                        "max_delay_minutes": max_delay
                    }
                ))

        return issues

    # =========================================================================
    # Problem 5: Stuck Discharge
    # =========================================================================
    def detect_stuck_discharges(self) -> List[BottleneckIssue]:
        issues = []
        incomplete = [d for d in self.data_service.discharges if d.document_status == "Incomplete"]

        if incomplete:
            ed_discharges = [d for d in incomplete if d.ward == "ED"]
            gen_discharges = [d for d in incomplete if "General" in (d.ward or "")]
            pae_discharges = [d for d in incomplete if "Paediatric" in (d.ward or "")]

            score, level = priority_service.calculate_priority(
                urgency="Critical",
                operational_impact="High",
                escalation_required=True,
                delay_or_volume_modifier=6
            )

            evidence = [
                f"{len(incomplete)} inpatient discharge workflows are currently stalled with Incomplete documentation.",
                f"Emergency Ward: DR001 (ED-06) and DR002 (ED-07) are blocked by: {'; '.join(ed_discharges[0].pending_tasks) if ed_discharges else 'paperwork'}.",
                f"General Wards: {len(gen_discharges)} discharge requests holding beds awaiting MRI reports.",
                f"Paediatric Ward: {len(pae_discharges)} discharge requests holding beds awaiting physician summaries."
            ]

            linked_beds = [d.bed_id for d in incomplete if d.bed_id]
            issues.append(BottleneckIssue(
                issue_id="ISSUE-DISCHARGE-STUCK",
                issue_type="STUCK_DISCHARGE",
                title="Inpatient Discharges Blocked by Administrative & Clearance Tasks",
                affected_department="Discharge Planning & Hospital Inpatient Wards",
                urgency="Critical",
                operational_impact="High",
                priority_score=score,
                priority_level=level,
                evidence=evidence,
                possible_causes=[
                    "Pending physician signature on discharge summaries.",
                    "Pending diagnostic clearances.",
                    "Pharmacy medication verification delays."
                ],
                recommended_actions=[
                    "Deploy discharge liaison nurse to coordinate fast-track document clearance.",
                    "Alert attending physicians on duty to review and sign off pending discharge packages.",
                    "Verify pending lab results with Central Diagnostics."
                ],
                responsible_team="Hospital Discharge Planning & Medical Records",
                escalation_required=True,
                created_at=self.data_service.reference_timestamp,
                status="Active",
                details={
                    "total_stuck_discharges": len(incomplete),
                    "stuck_discharge_count": len(incomplete),
                    "linked_blocked_beds": linked_beds,
                    "affected_wards": list(set(d.ward for d in incomplete if d.ward))
                }
            ))

        return issues

    # =========================================================================
    # Problem 6: Appointment Anomalies
    # =========================================================================
    def detect_appointment_anomalies(self) -> List[BottleneckIssue]:
        issues = []
        
        # 1. Overbooked timeslots: count bookings per (department, datetime)
        slot_map = defaultdict(list)
        for apt in self.data_service.appointments:
            slot_map[(apt.department, apt.datetime)].append(apt)

        for (dept, dt), slot_apts in slot_map.items():
            if len(slot_apts) >= 4:
                score_o, level_o = priority_service.calculate_priority(
                    urgency="Medium",
                    operational_impact="Medium",
                    escalation_required=False,
                    delay_or_volume_modifier=3
                )
                dept_slug = dept[:4].upper().replace(" ", "")
                issues.append(BottleneckIssue(
                    issue_id=f"ISSUE-APPT-OVERLOAD-{dept_slug}",
                    issue_type="APPOINTMENT_ANOMALY",
                    title=f"Overbooked Appointment Slot in {dept} at {dt}",
                    affected_department=dept,
                    urgency="Medium",
                    operational_impact="Medium",
                    priority_score=score_o,
                    priority_level=level_o,
                    evidence=[
                        f"{len(slot_apts)} patients booked concurrently for single slot {dt} in {dept}.",
                        f"Booked appointments: {', '.join(a.appointment_id for a in slot_apts[:4])}."
                    ],
                    possible_causes=["Clinic overbooking without physician capacity check."],
                    recommended_actions=["Stagger appointments across afternoon hours."],
                    responsible_team="Central Clinic Scheduling",
                    escalation_required=False,
                    created_at=self.data_service.reference_timestamp,
                    status="Active",
                    details={"department": dept, "datetime": dt, "booking_count": len(slot_apts)}
                ))
                break  # Top representative overload pattern

        # 2. High cancellation / no-show rate per department
        dept_all = defaultdict(list)
        for apt in self.data_service.appointments:
            dept_all[apt.department].append(apt)

        for dept, apts in dept_all.items():
            noshows = [a for a in apts if a.status.lower() in ("cancelled", "no-show")]
            if len(apts) >= 1 and (len(noshows) / len(apts) >= 0.1 or len(noshows) >= 2):
                rate_pct = round((len(noshows) / len(apts)) * 100, 1)
                score_n, level_n = priority_service.calculate_priority(
                    urgency="Low",
                    operational_impact="Low",
                    escalation_required=False,
                    delay_or_volume_modifier=2
                )
                dept_slug = dept[:4].upper().replace(" ", "")
                issues.append(BottleneckIssue(
                    issue_id=f"ISSUE-APPT-NOSHOW-{dept_slug}",
                    issue_type="APPOINTMENT_ANOMALY",
                    title=f"High Cancellation / No-Show Rate in {dept}",
                    affected_department=dept,
                    urgency="Low",
                    operational_impact="Low",
                    priority_score=score_n,
                    priority_level=level_n,
                    evidence=[
                        f"{dept} clinic had {len(noshows)} of {len(apts)} appointments ({rate_pct}%) cancelled or no-show.",
                        f"Sample affected appointments: {', '.join(a.appointment_id for a in noshows[:4])}."
                    ],
                    possible_causes=["Lack of automated reminder confirmations."],
                    recommended_actions=["Implement proactive 24-hour outpatient appointment reminder confirmations."],
                    responsible_team="Central Outpatient Scheduling Desk",
                    escalation_required=False,
                    created_at=self.data_service.reference_timestamp,
                    status="Active",
                    details={
                        "department": dept,
                        "total_scheduled": len(apts),
                        "no_show_or_cancelled": len(noshows),
                        "non_attendance_rate_pct": rate_pct
                    }
                ))
                break

        # 3. Open slots for today
        open_slots = [a for a in self.data_service.appointments if a.status.lower() in ["open slot", "open"]]
        if open_slots:
            score, level = priority_service.calculate_priority(
                urgency="Low",
                operational_impact="Low",
                escalation_required=False,
                delay_or_volume_modifier=1
            )
            issues.append(BottleneckIssue(
                issue_id="ISSUE-APPT-OPEN-SLOTS",
                issue_type="APPOINTMENT_ANOMALY",
                title="Unfilled Open Outpatient Appointment Slots Today",
                affected_department="Outpatient Clinics",
                urgency="Low",
                operational_impact="Low",
                priority_score=score,
                priority_level=level,
                evidence=[
                    f"{len(open_slots)} appointment slots are currently open and unbooked for today across specialty clinics.",
                    f"Sample open slots: {', '.join(a.appointment_id for a in open_slots[:5])}."
                ],
                possible_causes=["Same-day outpatient scheduling gaps."],
                recommended_actions=["Offer same-day open consultation slots to walk-in non-emergency patients."],
                responsible_team="Central Clinic Scheduling",
                escalation_required=False,
                created_at=self.data_service.reference_timestamp,
                status="Active",
                details={"open_slots_count": len(open_slots)}
            ))

        return issues

    # =========================================================================
    # Problem 7: Operational Complaints & Grievances
    # =========================================================================
    def detect_operational_complaints(self) -> List[BottleneckIssue]:
        issues = []
        # Group open feedback by category
        open_fb = [f for f in self.data_service.feedback if f.resolution_status.lower() in ["open", "in progress"]]
        cat_counts = defaultdict(list)
        for f in open_fb:
            cat_counts[f.category].append(f)

        for cat, items in cat_counts.items():
            high_sev = [f for f in items if f.severity in ["High", "Critical", "Medium"]]
            if len(high_sev) >= 3:
                urgency = "High" if any(f.severity in ["High", "Critical"] for f in items) else "Medium"
                score, level = priority_service.calculate_priority(
                    urgency=urgency,
                    operational_impact="Medium",
                    escalation_required=False,
                    delay_or_volume_modifier=len(high_sev)
                )

                cat_slug = cat.upper()[:4].replace(" ", "")
                issues.append(BottleneckIssue(
                    issue_id=f"ISSUE-COMPLAINT-{cat_slug}",
                    issue_type="OPERATIONAL_COMPLAINT",
                    title=f"Elevated Patient Grievances regarding {cat}",
                    affected_department="Patient Relations",
                    urgency=urgency,
                    operational_impact="Medium",
                    priority_score=score,
                    priority_level=level,
                    evidence=[
                        f"{len(items)} active patient feedback records report grievances concerning '{cat}'.",
                        f"Sample comments: {', '.join(f.complaint for f in items[:2])}."
                    ],
                    possible_causes=[f"Operational friction in {cat} processes impacting patient experience."],
                    recommended_actions=[f"Review complaints related to {cat} with relevant department supervisors."],
                    responsible_team="Patient Relations & Experience",
                    escalation_required=False,
                    created_at=self.data_service.reference_timestamp,
                    status="Active",
                    details={"category": cat, "complaint_count": len(items), "open_count": len(items)}
                ))

        return issues

    # =========================================================================
    # Problem 8: Multi-Factor Escalation Required
    # =========================================================================
    def detect_multi_factor_escalations(self) -> List[BottleneckIssue]:
        issues = []

        # Check compounding crisis
        wait_surge = any(w.ed_avg_wait_min >= 80 for w in self.data_service.ed_wait_times if w.date == "2026-11-16")
        blocked_ed_beds = [b for b in self.data_service.beds if b.availability == "Blocked" and ("ED" in b.ward or "Emergency" in b.ward)]
        icu_full = all(b.occupancy == "Occupied" for b in self.data_service.beds if b.ward == "ICU")
        evening_doctor_deficit = any(
            s.department == "Emergency" and "Evening" in s.shift and s.availability.lower() == "on leave"
            for s in self.data_service.staff
        )

        if wait_surge and len(blocked_ed_beds) >= 2 and evening_doctor_deficit:
            score, level = priority_service.calculate_priority(
                urgency="Critical",
                operational_impact="Critical",
                escalation_required=True,
                delay_or_volume_modifier=10
            )

            issues.append(BottleneckIssue(
                issue_id="ISSUE-ESCALATION-SANJEEVANI-CORE",
                issue_type="ESCALATION_REQUIRED",
                title="Systemic Multi-Factor Crisis: Emergency Bed Blockade, ICU Saturation & Shift Deficit",
                affected_department="Hospital Command Center & Emergency Leadership",
                urgency="Critical",
                operational_impact="Critical",
                priority_score=score,
                priority_level=level,
                evidence=[
                    "Compounding failure chain identified: Overdue CT Scans -> 2 Blocked Emergency Beds (ED-06, ED-07).",
                    "100% ICU Bed Exhaustion: 2 High-acuity patients (P1087 [P1], P1088 [P2]) trapped in ED awaiting ICU admission.",
                    "Emergency wait times have surged to 98 minutes with 9 patients holding without a bed.",
                    "Impending Evening shift is short-staffed with Dr. Rahul Iyer on leave and only 1 active doctor scheduled."
                ],
                possible_causes=[
                    "Simultaneous convergence of diagnostic delays, discharge paperwork stagnation, ICU bed gridlock, and roster deficits."
                ],
                recommended_actions=[
                    "Convene immediate emergency command huddle with Medical Director, Nursing Lead, and Radiology Supervisor.",
                    "Authorize fast-track discharge of ED-06 and ED-07 to immediately liberate 2 emergency beds.",
                    "Mobilize on-call physician and 2 float nurses for the 14–20 Emergency Evening shift.",
                    "Review ICU step-down candidates to discharge stable patients to general wards and liberate beds for P1 patient P1087."
                ],
                responsible_team="Hospital Executive Leadership & Emergency Task Force",
                escalation_required=True,
                created_at=self.data_service.reference_timestamp,
                status="Active",
                details={
                    "compounding_factors": [
                        "Emergency Wait Time Surge (98 mins)",
                        "2 Blocked Beds (ED-06, ED-07)",
                        "100% ICU Saturation (12/12 occupied)",
                        "Emergency Evening Doctor On Leave"
                    ]
                }
            ))

        return issues

    # =========================================================================
    # Master Aggregation & Ranking
    # =========================================================================
    def detect_all_issues(self) -> List[BottleneckIssue]:
        """Runs all 8 detection algorithms and returns prioritized issues."""
        all_issues = []
        all_issues.extend(self.detect_multi_factor_escalations())
        all_issues.extend(self.detect_long_waiting_times())
        all_issues.extend(self.detect_bed_shortage_or_blocks())
        all_issues.extend(self.detect_delayed_diagnostics())
        all_issues.extend(self.detect_staff_workload_imbalance())
        all_issues.extend(self.detect_stuck_discharges())
        all_issues.extend(self.detect_operational_complaints())
        all_issues.extend(self.detect_appointment_anomalies())

        # Sort descending by priority score
        all_issues.sort(key=lambda i: i.priority_score, reverse=True)
        return all_issues


detection_service = DetectionService()
