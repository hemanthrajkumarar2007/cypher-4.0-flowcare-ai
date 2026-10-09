"""
Unit tests for HospitalDataService and Data Quality Validation.
"""

import pytest
from services.data_service import HospitalDataService
from models import Bed, Admission


def test_data_service_loads_all_eight_categories():
    service = HospitalDataService()
    overview = service.get_overview()
    counts = overview["counts"]

    assert counts["patients"] > 0
    assert counts["appointments"] > 0
    assert counts["beds"] > 0
    assert counts["staff"] > 0
    assert counts["diagnostics"] > 0
    assert counts["admissions"] > 0
    assert counts["discharges"] > 0
    assert counts["feedback"] > 0
    assert overview["hospital"] == "Sanjeevani Multispeciality Hospital"


def test_data_filtering_queries():
    service = HospitalDataService()

    # Filter patients
    em_patients = service.get_patients(department="Emergency")
    assert all(p.department == "Emergency" for p in em_patients)
    assert len(em_patients) > 0

    # Filter appointments
    sched_apts = service.get_appointments(status="scheduled")
    assert all(a.status == "scheduled" for a in sched_apts)

    # Filter beds
    icu_beds = service.get_beds(ward="ICU Ward")
    assert all(b.ward == "ICU Ward" for b in icu_beds)
    assert len(icu_beds) == 4

    # Filter staff
    em_staff = service.get_staff(department="Emergency")
    assert all(s.department == "Emergency" for s in em_staff)


def test_baseline_synthetic_data_quality_is_valid():
    service = HospitalDataService()
    report = service.validate_data()
    assert report.is_valid is True
    assert report.total_records_checked > 30
    assert not any(i.severity == "Error" for i in report.issues)


def test_data_quality_detects_inconsistent_bed_state():
    service = HospitalDataService()
    # Inject inconsistent bed: Occupied but Available
    service.beds.append(Bed(
        bed_id="CORRUPT-BED-01",
        ward="Emergency Ward",
        bed_type="Emergency",
        occupancy="Occupied",
        availability="Available",  # Inconsistent!
        admission_discharge_status="Ready"
    ))

    report = service.validate_data()
    assert report.is_valid is False
    corrupt_issues = [i for i in report.issues if i.record_id == "CORRUPT-BED-01"]
    assert len(corrupt_issues) > 0
    assert corrupt_issues[0].issue_type == "State Inconsistency"


def test_data_quality_detects_invalid_references():
    service = HospitalDataService()
    # Inject admission with nonexistent patient
    service.admissions.append(Admission(
        admission_id="ADM-GHOST-01",
        patient_id="PATIENT-DOES-NOT-EXIST",
        admission_time="2026-10-10T08:00:00",
        department="General Medicine",
        ward="General Ward",
        bed_id="GEN-01",
        expected_discharge="2026-10-12T10:00:00",
        status="Active"
    ))

    report = service.validate_data()
    ghost_issues = [i for i in report.issues if i.record_id == "ADM-GHOST-01"]
    assert len(ghost_issues) > 0
    assert ghost_issues[0].issue_type == "Invalid Reference"
