"""
FlowCare AI — Data Repository & Quality Validation Service
Sanjeevani Multispeciality Hospital
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
    DataQualityReport,
    ValidationIssue,
)


class HospitalDataService:
    """Manages synthetic hospital data collections and performs relational validation."""

    def __init__(self, data_path: Optional[str] = None):
        if data_path:
            self.data_file = Path(data_path)
        else:
            self.data_file = Path(__file__).resolve().parent.parent / "data" / "synthetic_hospital_data.json"
        
        self.hospital_name: str = "Sanjeevani Multispeciality Hospital"
        self.reference_timestamp: str = "2026-10-10T10:00:00"
        self.patients: List[Patient] = []
        self.appointments: List[Appointment] = []
        self.beds: List[Bed] = []
        self.staff: List[Staff] = []
        self.diagnostics: List[Diagnostic] = []
        self.admissions: List[Admission] = []
        self.discharges: List[Discharge] = []
        self.feedback: List[Feedback] = []

        self.load_data()

    def load_data(self) -> None:
        """Loads data from the JSON seed file into memory."""
        if not self.data_file.exists():
            raise FileNotFoundError(f"Synthetic hospital data file not found at: {self.data_file}")

        with open(self.data_file, "r", encoding="utf-8") as f:
            raw = json.load(f)

        self.hospital_name = raw.get("hospital_name", "Sanjeevani Multispeciality Hospital")
        self.reference_timestamp = raw.get("reference_timestamp", "2026-10-10T10:00:00")

        self.patients = [Patient(**item) for item in raw.get("patients", [])]
        self.appointments = [Appointment(**item) for item in raw.get("appointments", [])]
        self.beds = [Bed(**item) for item in raw.get("beds", [])]
        self.staff = [Staff(**item) for item in raw.get("staff", [])]
        self.diagnostics = [Diagnostic(**item) for item in raw.get("diagnostics", [])]
        self.admissions = [Admission(**item) for item in raw.get("admissions", [])]
        self.discharges = [Discharge(**item) for item in raw.get("discharges", [])]
        self.feedback = [Feedback(**item) for item in raw.get("feedback", [])]

    def reset_to_default(self) -> None:
        """Reloads initial synthetic dataset from disk."""
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
            res = [s for s in res if s.shift.lower() == shift.lower()]
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
            res = [d for d in res if d.patient.lower() == patient.lower()]
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

    # =========================================================================
    # Data Quality & Validation Engine
    # =========================================================================

    def validate_data(self) -> DataQualityReport:
        """
        Validates referential integrity, state consistency, and timestamp sanity across all 8 datasets.
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
            try:
                datetime.fromisoformat(a.datetime)
            except Exception:
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
            if b.availability == "Blocked" and b.admission_discharge_status == "Ready":
                issues.append(ValidationIssue(
                    category="Beds",
                    record_id=b.bed_id,
                    issue_type="State Inconsistency",
                    description=f"Bed {b.bed_id} is Blocked but status is Ready for admission.",
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
            if dis.admission_id not in admission_ids:
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
        ref_dt = datetime.fromisoformat(self.reference_timestamp)
        for diag in self.diagnostics:
            if diag.patient not in patient_ids:
                issues.append(ValidationIssue(
                    category="Diagnostics",
                    record_id=diag.test_id,
                    issue_type="Invalid Reference",
                    description=f"Diagnostic order {diag.test_id} references nonexistent patient {diag.patient}.",
                    severity="Error"
                ))
            try:
                exp_dt = datetime.fromisoformat(diag.expected_completion)
                # Verify overdue status agrees with timestamp
                if diag.status != "completed" and exp_dt < ref_dt and diag.status != "overdue":
                    issues.append(ValidationIssue(
                        category="Diagnostics",
                        record_id=diag.test_id,
                        issue_type="State Inconsistency",
                        description=f"Diagnostic {diag.test_id} expected completion {diag.expected_completion} is past reference time but status is '{diag.status}'.",
                        severity="Warning"
                    ))
            except Exception:
                issues.append(ValidationIssue(
                    category="Diagnostics",
                    record_id=diag.test_id,
                    issue_type="Invalid Timestamp",
                    description=f"Diagnostic {diag.test_id} has invalid expected_completion timestamp.",
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
            try:
                datetime.fromisoformat(fb.timestamp)
            except Exception:
                issues.append(ValidationIssue(
                    category="Feedback",
                    record_id=fb.feedback_id,
                    issue_type="Invalid Timestamp",
                    description=f"Feedback {fb.feedback_id} has invalid timestamp.",
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

        has_errors = any(i.severity == "Error" for i in issues)

        return DataQualityReport(
            hospital=self.hospital_name,
            total_records_checked=total_records,
            is_valid=not has_errors,
            issue_count=len(issues),
            issues=issues,
            category_counts={
                "patients": len(self.patients),
                "appointments": len(self.appointments),
                "beds": len(self.beds),
                "staff": len(self.staff),
                "diagnostics": len(self.diagnostics),
                "admissions": len(self.admissions),
                "discharges": len(self.discharges),
                "feedback": len(self.feedback),
            }
        )


# Singleton instance for simple backend access
hospital_data_service = HospitalDataService()
