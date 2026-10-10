"""
FlowCare AI — Data Repository & Quality Validation Service
Sanjeevani Multispeciality Hospital
Cypher 2026 Hackathon — "The Blocked Bed" Challenge
"""

import json
from pathlib import Path
from datetime import datetime
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
    DataQualityReport,
    ValidationIssue,
)
from services.csv_service import HospitalCSVService


def parse_timestamp(ts: Optional[str]) -> Optional[datetime]:
    """Robust timestamp parser supporting ISO, space-separated, and date-only formats."""
    if not ts or not ts.strip():
        return None
    clean = ts.strip()
    for fmt in ["%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
        try:
            return datetime.strptime(clean, fmt)
        except ValueError:
            pass
    try:
        return datetime.fromisoformat(clean)
    except Exception:
        return None


class HospitalDataService:
    """Manages synthetic and real-time hospital data collections with relational validation."""

    def __init__(self, data_path: Optional[str] = None):
        self.backend_dir = Path(__file__).resolve().parent.parent
        self.csv_dir = self.backend_dir / "data" / "csv"
        self.json_file = Path(data_path) if data_path else (self.backend_dir / "data" / "synthetic_hospital_data.json")
        
        self.hospital_name: str = "Sanjeevani Multispeciality Hospital"
        self.reference_timestamp: str = "2026-11-16 10:00:00"
        self.patients: List[Patient] = []
        self.appointments: List[Appointment] = []
        self.beds: List[Bed] = []
        self.staff: List[Staff] = []
        self.diagnostics: List[Diagnostic] = []
        self.admissions: List[Admission] = []
        self.discharges: List[Discharge] = []
        self.feedback: List[Feedback] = []
        self.ed_wait_times: List[EDWaitTime] = []

        self.csv_loader = HospitalCSVService(csv_dir=self.csv_dir)
        self.load_data()

    def load_data(self) -> None:
        """Loads data preferentially from CSV files in data/csv/, falling back to JSON."""
        if self.csv_loader.has_csv_files():
            data = self.csv_loader.load_all_data()
            self.hospital_name = data.get("hospital_name", "Sanjeevani Multispeciality Hospital")
            self.reference_timestamp = data.get("reference_timestamp", "2026-11-16 10:00:00")
            self.patients = data.get("patients", [])
            self.appointments = data.get("appointments", [])
            self.beds = data.get("beds", [])
            self.staff = data.get("staff", [])
            self.diagnostics = data.get("diagnostics", [])
            self.admissions = data.get("admissions", [])
            self.discharges = data.get("discharges", [])
            self.feedback = data.get("feedback", [])
            self.ed_wait_times = data.get("ed_wait_times", [])

            # Sync in-memory records to JSON file as cache / backup
            self._save_json_cache()
            return

        if not self.json_file.exists():
            raise FileNotFoundError(f"Neither CSV data directory ({self.csv_dir}) nor JSON file ({self.json_file}) was found.")

        with open(self.json_file, "r", encoding="utf-8") as f:
            raw = json.load(f)

        self.hospital_name = raw.get("hospital_name", "Sanjeevani Multispeciality Hospital")
        self.reference_timestamp = raw.get("reference_timestamp", "2026-11-16 10:00:00")

        self.patients = [Patient(**item) for item in raw.get("patients", [])]
        self.appointments = [Appointment(**item) for item in raw.get("appointments", [])]
        self.beds = [Bed(**item) for item in raw.get("beds", [])]
        self.staff = [Staff(**item) for item in raw.get("staff", [])]
        self.diagnostics = [Diagnostic(**item) for item in raw.get("diagnostics", [])]
        self.admissions = [Admission(**item) for item in raw.get("admissions", [])]
        self.discharges = [Discharge(**item) for item in raw.get("discharges", [])]
        self.feedback = [Feedback(**item) for item in raw.get("feedback", [])]
        self.ed_wait_times = [EDWaitTime(**item) for item in raw.get("ed_wait_times", [])]

    def _save_json_cache(self) -> None:
        """Persists current state to JSON so both representations are identical."""
        try:
            payload = {
                "hospital_name": self.hospital_name,
                "reference_timestamp": self.reference_timestamp,
                "patients": [p.model_dump() for p in self.patients],
                "appointments": [a.model_dump() for a in self.appointments],
                "beds": [b.model_dump() for b in self.beds],
                "staff": [s.model_dump() for s in self.staff],
                "diagnostics": [d.model_dump() for d in self.diagnostics],
                "admissions": [adm.model_dump() for adm in self.admissions],
                "discharges": [dis.model_dump() for dis in self.discharges],
                "feedback": [f.model_dump() for f in self.feedback],
                "ed_wait_times": [w.model_dump() for w in self.ed_wait_times],
            }
            with open(self.json_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
        except Exception:
            pass

    def reset_to_default(self) -> None:
        """Reloads initial hospital dataset from disk."""
        self.load_data()

    def get_overview(self) -> Dict[str, Any]:
        """Returns record counts by category."""
        return {
            "hospital": self.hospital_name,
            "reference_timestamp": self.reference_timestamp,
            "counts": {
                "patients": len(self.patients),
                "appointments": len(self.appointments),
                "beds": len(self.beds),
                "staff": len(self.staff),
                "diagnostics": len(self.diagnostics),
                "admissions": len(self.admissions),
                "discharges": len(self.discharges),
                "feedback": len(self.feedback),
                "ed_wait_times": len(self.ed_wait_times),
            }
        }

    # =========================================================================
    # Query & Filter Methods
    # =========================================================================

    def get_patients(
        self,
        department: Optional[str] = None,
        status: Optional[str] = None,
        age_group: Optional[str] = None,
        visit_type: Optional[str] = None
    ) -> List[Patient]:
        res = self.patients
        if department:
            res = [p for p in res if p.department.lower() == department.lower()]
        if status:
            res = [p for p in res if p.status.lower() == status.lower()]
        if age_group:
            res = [p for p in res if p.age_group.lower() == age_group.lower()]
        if visit_type:
            res = [p for p in res if p.visit_type.lower() == visit_type.lower()]
        return res

    def get_appointments(
        self,
        department: Optional[str] = None,
        doctor: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Appointment]:
        res = self.appointments
        if department:
            res = [a for a in res if a.department.lower() == department.lower()]
        if doctor:
            res = [a for a in res if doctor.lower() in a.doctor.lower()]
        if status:
            res = [a for a in res if a.status.lower() == status.lower()]
        return res

    def get_beds(
        self,
        ward: Optional[str] = None,
        bed_type: Optional[str] = None,
        occupancy: Optional[str] = None,
        availability: Optional[str] = None
    ) -> List[Bed]:
        res = self.beds
        if ward:
            res = [b for b in res if ward.lower() in b.ward.lower()]
        if bed_type:
            res = [b for b in res if b.bed_type.lower() == bed_type.lower()]
        if occupancy:
            res = [b for b in res if b.occupancy.lower() == occupancy.lower()]
        if availability:
            res = [b for b in res if b.availability.lower() == availability.lower()]
        return res

    def get_bed_by_id(self, bed_id: str) -> Optional[Bed]:
        for b in self.beds:
            if b.bed_id.lower() == bed_id.lower():
                return b
        return None

    def update_bed(
        self,
        bed_id: str,
        availability: Optional[str] = None,
        occupancy: Optional[str] = None,
        admission_discharge_status: Optional[str] = None,
        patient_id: Optional[str] = None,
        blocked_reason: Optional[str] = None
    ) -> Optional[Bed]:
        bed = self.get_bed_by_id(bed_id)
        if not bed:
            return None

        if availability is not None:
            bed.availability = availability
            # Maintain logical consistency
            if availability.lower() == "available":
                bed.occupancy = "Unoccupied"
                bed.admission_discharge_status = admission_discharge_status or "Available"
                bed.blocked_reason = None
                bed.patient_id = None
            elif availability.lower() == "occupied":
                bed.occupancy = "Occupied"
                bed.admission_discharge_status = admission_discharge_status or "Occupied"
            elif availability.lower() == "blocked":
                bed.admission_discharge_status = admission_discharge_status or "Discharge Paperwork Blocked"
                if blocked_reason:
                    bed.blocked_reason = blocked_reason
            elif availability.lower() == "cleaning":
                bed.occupancy = "Unoccupied"
                bed.admission_discharge_status = admission_discharge_status or "Cleaning Required"
                bed.blocked_reason = None
                bed.patient_id = None

        if occupancy is not None:
            bed.occupancy = occupancy

        if admission_discharge_status is not None:
            bed.admission_discharge_status = admission_discharge_status

        if patient_id is not None:
            if patient_id.strip() == "" or patient_id.lower() in ("none", "null"):
                bed.patient_id = None
            else:
                bed.patient_id = patient_id.strip()
                bed.occupancy = "Occupied"
                bed.availability = "Occupied"
                bed.admission_discharge_status = "Admitted"
                # Update corresponding patient record if found
                for p in self.patients:
                    if p.patient_id.lower() == patient_id.strip().lower():
                        p.status = "In bed"

        if blocked_reason is not None:
            bed.blocked_reason = blocked_reason

        return bed

    def get_staff(
        self,
        department: Optional[str] = None,
        shift: Optional[str] = None,
        availability: Optional[str] = None,
        role: Optional[str] = None
    ) -> List[Staff]:
        res = self.staff
        if department:
            res = [s for s in res if s.department.lower() == department.lower()]
        if shift:
            res = [s for s in res if shift.lower() in s.shift.lower()]
        if availability:
            res = [s for s in res if s.availability.lower() == availability.lower()]
        if role:
            res = [s for s in res if s.role.lower() == role.lower()]
        return res

    def get_diagnostics(
        self,
        status: Optional[str] = None,
        department: Optional[str] = None,
        patient: Optional[str] = None
    ) -> List[Diagnostic]:
        res = self.diagnostics
        if status:
            res = [d for d in res if d.status.lower() == status.lower()]
        if department:
            res = [d for d in res if d.department.lower() == department.lower()]
        if patient:
            res = [d for d in res if d.patient.lower() == patient.lower() or (d.patient_id and d.patient_id.lower() == patient.lower())]
        return res

    def get_admissions(
        self,
        department: Optional[str] = None,
        ward: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Admission]:
        res = self.admissions
        if department:
            res = [a for a in res if a.department.lower() == department.lower()]
        if ward:
            res = [a for a in res if ward.lower() in a.ward.lower()]
        if status:
            res = [a for a in res if a.status.lower() == status.lower()]
        return res

    def get_discharges(
        self,
        request_status: Optional[str] = None,
        document_status: Optional[str] = None
    ) -> List[Discharge]:
        res = self.discharges
        if request_status:
            res = [d for d in res if d.request.lower() == request_status.lower()]
        if document_status:
            res = [d for d in res if d.document_status.lower() == document_status.lower()]
        return res

    def get_feedback(
        self,
        category: Optional[str] = None,
        severity: Optional[str] = None,
        department: Optional[str] = None,
        resolution_status: Optional[str] = None
    ) -> List[Feedback]:
        res = self.feedback
        if category:
            res = [f for f in res if category.lower() in f.category.lower()]
        if severity:
            res = [f for f in res if f.severity.lower() == severity.lower()]
        if department:
            res = [f for f in res if f.department and f.department.lower() == department.lower()]
        if resolution_status:
            res = [f for f in res if f.resolution_status.lower() == resolution_status.lower()]
        return res

    def get_ed_wait_times(self, date: Optional[str] = None) -> List[EDWaitTime]:
        res = self.ed_wait_times
        if date:
            res = [w for w in res if w.date == date]
        return res

    # =========================================================================
    # Data Quality & Validation Engine
    # =========================================================================

    def validate_data(self) -> DataQualityReport:
        """
        Validates referential integrity, state consistency, and timestamp sanity across all datasets.
        Returns a DataQualityReport.
        """
        issues: List[ValidationIssue] = []

        patient_ids = {p.patient_id for p in self.patients}
        admission_ids = {a.admission_id for a in self.admissions}
        bed_ids = {b.bed_id for b in self.beds}

        # 1. Patients check
        for p in self.patients:
            if not p.patient_id or not p.department or not p.status:
                issues.append(ValidationIssue(
                    category="Patients",
                    record_id=p.patient_id or "unknown",
                    issue_type="Missing Field",
                    description="Patient record missing required fields.",
                    severity="Error"
                ))

        # 2. Appointments check
        for a in self.appointments:
            dt = parse_timestamp(a.datetime)
            if not dt:
                issues.append(ValidationIssue(
                    category="Appointments",
                    record_id=a.appointment_id,
                    issue_type="Invalid Timestamp",
                    description=f"Appointment {a.appointment_id} has invalid datetime: {a.datetime}",
                    severity="Error"
                ))

        # 3. Beds consistency check
        for b in self.beds:
            # Rule: Occupied bed cannot be marked Available
            if b.occupancy == "Occupied" and b.availability == "Available":
                issues.append(ValidationIssue(
                    category="Beds",
                    record_id=b.bed_id,
                    issue_type="State Inconsistency",
                    description=f"Bed {b.bed_id} is marked Occupied but availability is Available.",
                    severity="Error"
                ))
            # Rule: Blocked bed cannot be presented as ready for new admission
            if b.availability == "Blocked" and b.admission_discharge_status in ["Ready", "Available"]:
                issues.append(ValidationIssue(
                    category="Beds",
                    record_id=b.bed_id,
                    issue_type="State Inconsistency",
                    description=f"Bed {b.bed_id} is Blocked but status is ready for admission.",
                    severity="Error"
                ))
            # Rule: Blocked bed should have an identifiable reason
            if b.availability == "Blocked" and not b.blocked_reason:
                issues.append(ValidationIssue(
                    category="Beds",
                    record_id=b.bed_id,
                    issue_type="Missing Field",
                    description=f"Bed {b.bed_id} is Blocked but lacks a blocked_reason.",
                    severity="Warning"
                ))
            # Rule: If bed has current_admission_id, it must exist
            if b.current_admission_id and b.current_admission_id not in admission_ids:
                issues.append(ValidationIssue(
                    category="Beds",
                    record_id=b.bed_id,
                    issue_type="Invalid Reference",
                    description=f"Bed {b.bed_id} references nonexistent admission {b.current_admission_id}.",
                    severity="Error"
                ))

        # 4. Admissions check
        for adm in self.admissions:
            if adm.patient_id not in patient_ids:
                issues.append(ValidationIssue(
                    category="Admissions",
                    record_id=adm.admission_id,
                    issue_type="Invalid Reference",
                    description=f"Admission {adm.admission_id} references nonexistent patient {adm.patient_id}.",
                    severity="Error"
                ))
            if adm.bed_id and adm.bed_id not in bed_ids:
                issues.append(ValidationIssue(
                    category="Admissions",
                    record_id=adm.admission_id,
                    issue_type="Invalid Reference",
                    description=f"Admission {adm.admission_id} references nonexistent bed {adm.bed_id}.",
                    severity="Error"
                ))

        # 5. Discharges check
        for dis in self.discharges:
            if dis.admission_id and dis.admission_id not in admission_ids:
                issues.append(ValidationIssue(
                    category="Discharge",
                    record_id=dis.discharge_id,
                    issue_type="Invalid Reference",
                    description=f"Discharge {dis.discharge_id} references nonexistent admission {dis.admission_id}.",
                    severity="Error"
                ))
            if dis.patient_id not in patient_ids:
                issues.append(ValidationIssue(
                    category="Discharge",
                    record_id=dis.discharge_id,
                    issue_type="Invalid Reference",
                    description=f"Discharge {dis.discharge_id} references nonexistent patient {dis.patient_id}.",
                    severity="Error"
                ))

        # 6. Diagnostics check
        ref_dt = parse_timestamp(self.reference_timestamp)
        for diag in self.diagnostics:
            if diag.patient not in patient_ids:
                issues.append(ValidationIssue(
                    category="Diagnostics",
                    record_id=diag.test_id,
                    issue_type="Invalid Reference",
                    description=f"Diagnostic order {diag.test_id} references nonexistent patient {diag.patient}.",
                    severity="Error"
                ))
            exp_dt = parse_timestamp(diag.expected_completion)
            if not exp_dt:
                issues.append(ValidationIssue(
                    category="Diagnostics",
                    record_id=diag.test_id,
                    issue_type="Invalid Timestamp",
                    description=f"Diagnostic {diag.test_id} has invalid expected_completion timestamp: {diag.expected_completion}",
                    severity="Error"
                ))

        # 7. Staff check
        for stf in self.staff:
            if not stf.staff_id or not stf.name or not stf.role:
                issues.append(ValidationIssue(
                    category="Staff",
                    record_id=stf.staff_id,
                    issue_type="Missing Field",
                    description="Staff record has missing essential attributes.",
                    severity="Error"
                ))

        # 8. Feedback check
        for fb in self.feedback:
            fb_dt = parse_timestamp(fb.timestamp)
            if not fb_dt:
                issues.append(ValidationIssue(
                    category="Feedback",
                    record_id=fb.feedback_id,
                    issue_type="Invalid Timestamp",
                    description=f"Feedback {fb.feedback_id} has invalid timestamp: {fb.timestamp}",
                    severity="Error"
                ))

        total_records = (
            len(self.patients) +
            len(self.appointments) +
            len(self.beds) +
            len(self.staff) +
            len(self.diagnostics) +
            len(self.admissions) +
            len(self.discharges) +
            len(self.feedback)
        )

        error_count = sum(1 for i in issues if i.severity == "Error")

        category_counts = {
            "patients": len(self.patients),
            "appointments": len(self.appointments),
            "beds": len(self.beds),
            "staff": len(self.staff),
            "diagnostics": len(self.diagnostics),
            "admissions": len(self.admissions),
            "discharges": len(self.discharges),
            "feedback": len(self.feedback),
        }

        return DataQualityReport(
            hospital=self.hospital_name,
            total_records_checked=total_records,
            is_valid=(error_count == 0),
            issue_count=len(issues),
            issues=issues,
            category_counts=category_counts
        )


hospital_data_service = HospitalDataService()
