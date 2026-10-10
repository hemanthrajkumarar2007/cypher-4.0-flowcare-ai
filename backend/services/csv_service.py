"""
FlowCare AI — CSV Data Ingestion & Cross-Reference Service
Loads and connects all 9 Challenge 05 CSV datasets for Sanjeevani Multispeciality Hospital.
"""

import csv
from pathlib import Path
from typing import List, Dict, Any, Optional

from models import (
    Patient,
    Appointment,
    Bed,
    Staff,
    Diagnostic,
    Admission,
    Discharge,
    Feedback,
    EDWaitTime,
)


class HospitalCSVService:
    """Loads, validates, and interlinks the 9 official Challenge 05 CSV files."""

    def __init__(self, csv_dir: Optional[Path] = None):
        if csv_dir:
            self.csv_dir = Path(csv_dir)
        else:
            self.csv_dir = Path(__file__).resolve().parent.parent / "data" / "csv"
        
        self.reference_timestamp = "2026-11-16 10:00:00"

    def has_csv_files(self) -> bool:
        """Checks if the required CSV files exist."""
        required = ["patients.csv", "beds.csv", "appointments.csv"]
        return all((self.csv_dir / f).exists() for f in required)

    def _read_csv(self, filename: str) -> List[Dict[str, str]]:
        file_path = self.csv_dir / filename
        if not file_path.exists():
            # Check for alternative filename e.g. discharge.csv vs discharges.csv
            alt_name = "discharge.csv" if filename == "discharges.csv" else "discharges.csv"
            alt_path = self.csv_dir / alt_name
            if alt_path.exists():
                file_path = alt_path
            else:
                return []
        
        with open(file_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            return [dict(row) for row in reader]

    def load_all_data(self) -> Dict[str, Any]:
        """Loads and interlinks all hospital records from CSV."""
        # 1. Patients
        patients_raw = self._read_csv("patients.csv")
        patients: List[Patient] = []
        for r in patients_raw:
            patients.append(Patient(
                patient_id=r["patient_id"].strip(),
                age_group=r["age_group"].strip(),
                department=r["department"].strip(),
                visit_type=r["visit_type"].strip(),
                status=r["status"].strip()
            ))

        # 2. Admissions
        admissions_raw = self._read_csv("admissions.csv")
        admissions: List[Admission] = []
        patient_to_admission: Dict[str, str] = {}
        for r in admissions_raw:
            adm_id = r["admission_id"].strip()
            p_id = r["patient_id"].strip()
            patient_to_admission[p_id] = adm_id
            admissions.append(Admission(
                admission_id=adm_id,
                patient_id=p_id,
                admission_time=r["admission_time"].strip(),
                department=r["department"].strip(),
                ward=r["ward"].strip(),
                bed_id=None,  # Linked later from beds
                expected_discharge=r.get("expected_discharge", "").strip() or None,
                status=r["status"].strip(),
                triage_priority=r.get("triage_priority", "").strip() or None
            ))

        # 3. Discharges
        discharges_raw = self._read_csv("discharges.csv")
        discharges: List[Discharge] = []
        bed_to_discharge: Dict[str, Discharge] = {}
        patient_to_discharge: Dict[str, Discharge] = {}
        for r in discharges_raw:
            req_id = r["request_id"].strip()
            p_id = r["patient_id"].strip()
            b_id = r.get("bed_id", "").strip()
            tasks_raw = r.get("pending_tasks", "")
            tasks = [t.strip() for t in tasks_raw.split(";") if t.strip()]

            d = Discharge(
                discharge_id=req_id,
                request_id=req_id,
                admission_id=patient_to_admission.get(p_id, f"ADM-{p_id}"),
                patient_id=p_id,
                ward=r.get("ward", "").strip() or None,
                bed_id=b_id or None,
                request="Pending",
                pending_tasks=tasks,
                medication_status=r.get("medication_status", "Pending").strip(),
                document_status=r.get("document_status", "Incomplete").strip(),
                discharge_initiated_at=r.get("requested_time", "").strip() or None,
                requested_time=r.get("requested_time", "").strip() or None
            )
            discharges.append(d)
            if b_id:
                bed_to_discharge[b_id] = d
            patient_to_discharge[p_id] = d

        # 4. Beds
        beds_raw = self._read_csv("beds.csv")
        beds: List[Bed] = []
        for r in beds_raw:
            b_id = r["bed_id"].strip()
            ward = r["ward"].strip()
            b_type = r["bed_type"].strip()
            occ = r["occupancy"].strip()
            p_id = r.get("patient_id", "").strip() or None
            status = r["admission_discharge_status"].strip()

            # Determine availability
            if occ == "Occupied":
                if status in ["Discharge pending", "Blocked", "Discharge delayed"]:
                    avail = "Blocked"
                else:
                    avail = "Occupied"
            else:
                if status in ["Cleaning", "Cleaning required"]:
                    avail = "Cleaning"
                else:
                    avail = "Available"

            # Determine blocked reason
            blocked_reason = None
            if avail == "Blocked":
                dis = bed_to_discharge.get(b_id) or (patient_to_discharge.get(p_id) if p_id else None)
                if dis and dis.pending_tasks:
                    blocked_reason = f"Discharge pending: {'; '.join(dis.pending_tasks)}"
                else:
                    blocked_reason = "Pending discharge sign-off and report clearance"

            # Current admission ID
            curr_adm_id = patient_to_admission.get(p_id) if p_id else None

            # Link bed ID back to admission
            if p_id and curr_adm_id:
                for adm in admissions:
                    if adm.admission_id == curr_adm_id:
                        adm.bed_id = b_id

            beds.append(Bed(
                bed_id=b_id,
                ward=ward,
                bed_type=b_type,
                occupancy=occ,
                availability=avail,
                admission_discharge_status=status,
                patient_id=p_id,
                current_admission_id=curr_adm_id,
                blocked_reason=blocked_reason
            ))

        # 5. Diagnostics
        diagnostics_raw = self._read_csv("diagnostics.csv")
        diagnostics: List[Diagnostic] = []
        for r in diagnostics_raw:
            t_id = r["test_id"].strip()
            p_id = r["patient_id"].strip()
            dept = r["department"].strip()
            status = r["status"].strip()
            req_time = r["requested_time"].strip()
            exp_time = r["expected_completion"].strip()

            # Check if overdue relative to snapshot
            is_overdue = False
            if status.lower() in ["report pending", "pending", "in progress", "requested"]:
                if exp_time and exp_time < self.reference_timestamp:
                    is_overdue = True

            diagnostics.append(Diagnostic(
                test_id=t_id,
                test=r["test"].strip(),
                patient=p_id,
                patient_id=p_id,
                department=dept,
                status="overdue" if is_overdue else status,
                requested_time=req_time,
                expected_completion=exp_time,
                completed_time=None if status.lower() != "completed" else exp_time,
                is_overdue=is_overdue
            ))

        # 6. Appointments
        appointments_raw = self._read_csv("appointments.csv")
        appointments: List[Appointment] = []
        for r in appointments_raw:
            apt_id = r["appointment_id"].strip()
            doctor = r["doctor"].strip()
            dept = r["department"].strip()
            dt = r["datetime"].strip()
            raw_st = r["status"].strip()
            st = raw_st.lower() if raw_st.lower() in ["scheduled", "completed", "cancelled", "no-show"] else raw_st
            
            # Parse waiting time min
            wait_raw = r.get("waiting_time_min", "").strip()
            wait_min = 0.0
            if wait_raw:
                try:
                    wait_min = float(wait_raw)
                except ValueError:
                    wait_min = 0.0

            appointments.append(Appointment(
                appointment_id=apt_id,
                doctor=doctor,
                department=dept,
                datetime=dt,
                status=st,
                waiting_time=int(round(wait_min)),
                waiting_time_min=wait_min
            ))

        # 7. Staff
        staff_raw = self._read_csv("staff.csv")
        staff: List[Staff] = []
        for r in staff_raw:
            stf_id = r["staff_id"].strip()
            name = r["name"].strip()
            role = r["role"].strip()
            dept = r["department"].strip()
            dt = r.get("date", "").strip() or None
            shift = r["shift"].strip()
            avail = r["availability"].strip()

            assigned_raw = r.get("patients_assigned", "").strip()
            assigned = int(assigned_raw) if assigned_raw.isdigit() else 0

            # Derive workload
            if avail.lower() == "on leave":
                workload = "Unavailable"
            elif assigned >= 25:
                workload = "Critical"
            elif assigned >= 15:
                workload = "High"
            elif assigned >= 6:
                workload = "Normal"
            else:
                workload = "Low"

            staff.append(Staff(
                staff_id=stf_id,
                name=name,
                role=role,
                department=dept,
                date=dt,
                shift=shift,
                availability=avail,
                patients_assigned=assigned,
                workload=workload
            ))

        # 8. Feedback
        feedback_raw = self._read_csv("feedback.csv")
        feedback: List[Feedback] = []
        for r in feedback_raw:
            f_id = r["feedback_id"].strip()
            dt = r.get("date", "").strip()
            dept = r.get("department", "").strip() or None
            cat = r["category"].strip()
            sev = r["severity"].strip()
            res_st = r["resolution_status"].strip()
            comment = r.get("comment", "").strip()

            complaint = comment if comment else f"{sev} {cat} issue reported in {dept or 'hospital'}."

            feedback.append(Feedback(
                feedback_id=f_id,
                complaint=complaint,
                comment=comment or None,
                category=cat,
                department=dept,
                severity=sev,
                resolution_status=res_st,
                timestamp=f"{dt}T10:00:00" if dt else "2026-11-16T10:00:00",
                date=dt or None
            ))

        # 9. ED Wait Times
        ed_wait_raw = self._read_csv("ed_wait_times.csv")
        ed_wait_times: List[EDWaitTime] = []
        for r in ed_wait_raw:
            ed_wait_times.append(EDWaitTime(
                date=r["date"].strip(),
                hour=r["hour"].strip(),
                ed_avg_wait_min=int(float(r["ed_avg_wait_min"].strip()))
            ))

        return {
            "hospital_name": "Sanjeevani Multispeciality Hospital",
            "reference_timestamp": self.reference_timestamp,
            "patients": patients,
            "appointments": appointments,
            "beds": beds,
            "staff": staff,
            "diagnostics": diagnostics,
            "admissions": admissions,
            "discharges": discharges,
            "feedback": feedback,
            "ed_wait_times": ed_wait_times,
        }
