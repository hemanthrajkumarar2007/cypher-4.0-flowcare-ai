/**
 * FlowCare AI — TypeScript Domain Definitions
 * Matches FastAPI models for Sanjeevani Multispeciality Hospital
 */

export interface Patient {
  patient_id: string;
  age_group: string;
  department: string;
  visit_type: string;
  status: string;
}

export interface Appointment {
  appointment_id: string;
  doctor: string;
  department: string;
  datetime: string;
  status: 'scheduled' | 'completed' | 'cancelled' | 'no-show' | string;
  waiting_time: number;
}

export interface Bed {
  bed_id: string;
  ward: string;
  bed_type: 'Emergency' | 'ICU' | 'General' | 'Step-down' | string;
  occupancy: 'Occupied' | 'Unoccupied' | string;
  availability: 'Available' | 'Occupied' | 'Blocked' | 'Cleaning' | string;
  admission_discharge_status: string;
  current_admission_id?: string | null;
  blocked_reason?: string | null;
}

export interface Staff {
  staff_id: string;
  name: string;
  role: 'Doctor' | 'Nurse' | 'Support Staff' | 'Technician' | string;
  department: string;
  shift: 'Morning' | 'Evening' | 'Night' | string;
  availability: 'Available' | 'On Duty' | 'On Break' | 'Unavailable' | 'On Leave' | string;
  workload: 'Low' | 'Normal' | 'High' | 'Critical' | string;
}

export interface Diagnostic {
  test_id: string;
  test: string;
  patient: string;
  department: string;
  status: 'pending' | 'in-progress' | 'completed' | 'overdue' | string;
  requested_time: string;
  expected_completion: string;
  completed_time?: string | null;
}

export interface Admission {
  admission_id: string;
  patient_id: string;
  admission_time: string;
  department: string;
  ward: string;
  bed_id?: string | null;
  expected_discharge: string;
  status: 'Active' | 'Discharging' | 'Discharged' | string;
}

export interface Discharge {
  discharge_id: string;
  admission_id: string;
  patient_id: string;
  request: 'Pending' | 'Approved' | 'In Review' | string;
  pending_tasks: string[];
  medication_status: string;
  document_status: 'Incomplete' | 'Pending Signature' | 'Cleared' | string;
  discharge_initiated_at: string;
}

export interface Feedback {
  feedback_id: string;
  complaint: string;
  category: string;
  department?: string | null;
  severity: 'Low' | 'Medium' | 'High' | 'Critical' | string;
  resolution_status: string;
  timestamp: string;
}

export interface ValidationIssue {
  category: string;
  record_id?: string | null;
  issue_type: string;
  description: string;
  severity: 'Warning' | 'Error' | string;
}

export interface DataQualityReport {
  hospital: string;
  total_records_checked: number;
  is_valid: boolean;
  issue_count: number;
  issues: ValidationIssue[];
  category_counts: Record<string, number>;
}

export interface BottleneckIssue {
  issue_id: string;
  issue_type: string;
  title: string;
  affected_department: string;
  urgency: 'Low' | 'Medium' | 'High' | 'Critical';
  operational_impact: 'Low' | 'Medium' | 'High' | 'Critical';
  priority_score: number;
  priority_level: 'Low' | 'Medium' | 'High' | 'Critical';
  evidence: string[];
  possible_causes: string[];
  recommended_actions: string[];
  responsible_team: string;
  escalation_required: boolean;
  created_at: string;
  status: string;
  details: Record<string, any>;
}

export interface CausalLink {
  link_id: string;
  source_issue_id: string;
  target_issue_id: string;
  source_department: string;
  target_department: string;
  relationship_type: string;
  supporting_evidence: string[];
  explanation: string;
  confidence: 'High' | 'Medium' | 'Moderate' | string;
  uncertainty_note: string;
}

export interface Recommendation {
  recommendation_id: string;
  related_issue_id: string;
  category: string;
  proposed_action: string;
  reason: string;
  supporting_evidence: string[];
  responsible_team: string;
  priority: 'Low' | 'Medium' | 'High' | 'Critical';
  review_status: string;
}

export interface SimulatedAction {
  action_id: string;
  recommendation_id: string;
  related_issue_id: string;
  action_type: string;
  title: string;
  description: string;
  responsible_team: string;
  target_department: string;
  priority: string;
  status: 'Awaiting review' | 'Approved' | 'Rejected' | 'Completed' | string;
  created_at: string;
  updated_at: string;
  created_by: string;
  reviewed_by?: string | null;
  review_notes?: string | null;
  completed_at?: string | null;
}

export interface ActionCreateRequest {
  recommendation_id: string;
  related_issue_id: string;
  proposed_action: string;
  responsible_team: string;
  target_department: string;
  priority?: string;
  notes?: string;
}

export interface ActionReviewRequest {
  status: 'Approved' | 'Rejected';
  reviewer_label: string;
  notes?: string;
}

export interface ActionCompleteRequest {
  reviewer_label: string;
  notes?: string;
}

export interface AuditLogEntry {
  audit_id: string;
  action_id: string;
  previous_status: string;
  new_status: string;
  timestamp: string;
  reviewer_label: string;
  notes?: string | null;
}

export interface DashboardSummary {
  hospital: string;
  timestamp: string;
  total_beds: number;
  occupied_beds: number;
  available_beds: number;
  blocked_beds: number;
  cleaning_beds: number;
  occupancy_rate_pct: number;
  overdue_diagnostics_count: number;
  active_bottlenecks_count: number;
  critical_issues_count: number;
  pending_actions_count: number;
  top_departments_needing_attention: string[];
  priority_queue_summary: Array<{
    issue_id: string;
    title: string;
    department: string;
    priority_level: string;
    priority_score: number;
    escalation_required: boolean;
  }>;
}

export type NavigationTab =
  | 'overview'
  | 'bottlenecks'
  | 'beds'
  | 'diagnostics'
  | 'discharges'
  | 'staff-appointments'
  | 'causal-links'
  | 'priority-queue'
  | 'actions-audit'
  | 'data-quality';
