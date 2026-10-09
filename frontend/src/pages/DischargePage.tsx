import React from 'react';
import { LogOut, FileText, CheckCircle2, AlertOctagon, Clock, Bed } from 'lucide-react';
import { Discharge, Admission, Bed as BedType } from '../types';
import { Badge } from '../components/Badge';

interface DischargePageProps {
  discharges: Discharge[];
  admissions: Admission[];
  beds: BedType[];
  loading: boolean;
}

export const DischargePage: React.FC<DischargePageProps> = ({
  discharges,
  admissions,
  beds,
  loading,
}) => {
  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '60vh' }}>
        <div className="spinner" style={{ width: 40, height: 40 }} />
      </div>
    );
  }

  // Correlate discharge with admission and bed
  const dischargeCards = discharges.map((dis) => {
    const adm = admissions.find((a) => a.admission_id === dis.admission_id);
    const bed = beds.find((b) => b.current_admission_id === dis.admission_id || b.bed_id === adm?.bed_id);
    return {
      discharge: dis,
      admission: adm,
      bed: bed,
    };
  });

  return (
    <div>
      {/* Information Banner */}
      <div className="alert-box alert-danger">
        <AlertOctagon size={18} color="#dc2626" style={{ flexShrink: 0, marginTop: 2 }} />
        <div>
          <strong>Discharge Clearance Bottleneck:</strong> Inpatients who are clinically recovered remain physically in hospital beds purely awaiting
          administrative clearance tasks (insurance billing approval, pharmacy counseling, and physician summary sign-off).
          A bed transitions to <em>Cleaning</em> and then <em>Available</em> only after authorized discharge processing is finalized.
        </div>
      </div>

      {/* Discharge Cards */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {dischargeCards.map(({ discharge, admission, bed }) => {
          const isIncomplete = discharge.document_status !== 'Cleared';
          return (
            <div
              key={discharge.discharge_id}
              className="card"
              style={{
                borderLeft: `5px solid ${isIncomplete ? '#dc2626' : '#16a34a'}`,
                background: isIncomplete ? '#fffafa' : '#ffffff',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                    <span style={{ fontSize: '0.8rem', fontWeight: 700, fontFamily: 'monospace', color: '#64748b' }}>
                      {discharge.discharge_id}
                    </span>
                    <Badge
                      label={`Document: ${discharge.document_status}`}
                      variant={discharge.document_status === 'Cleared' ? 'available' : 'critical'}
                    />
                    <Badge label={`Request: ${discharge.request}`} variant="high" />
                  </div>
                  <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#0f172a' }}>
                    Patient: {discharge.patient_id} (Admission: {discharge.admission_id})
                  </h3>
                </div>

                {/* Linked Bed Badge */}
                {bed && (
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      background: '#fef2f2',
                      border: '1px solid #fecaca',
                      padding: '0.4rem 0.75rem',
                      borderRadius: '6px',
                    }}
                  >
                    <Bed size={16} color="#dc2626" />
                    <div>
                      <div style={{ fontSize: '0.7rem', color: '#991b1b', fontWeight: 600 }}>BLOCKING BED</div>
                      <div style={{ fontSize: '0.95rem', fontWeight: 800, color: '#dc2626' }}>{bed.bed_id}</div>
                    </div>
                  </div>
                )}
              </div>

              {/* Admission Info */}
              <div
                style={{
                  display: 'flex',
                  gap: '1.5rem',
                  fontSize: '0.8rem',
                  color: '#64748b',
                  marginBottom: '1rem',
                  background: '#f8fafc',
                  padding: '0.5rem 0.75rem',
                  borderRadius: '6px',
                }}
              >
                <span>Department: <strong>{admission?.department || 'Emergency'}</strong></span>
                <span>Ward: <strong>{admission?.ward || 'Emergency Ward'}</strong></span>
                <span>Discharge Initiated: <strong>{discharge.discharge_initiated_at.replace('T', ' ')}</strong></span>
                <span>Medication Status (Operational): <strong>{discharge.medication_status}</strong></span>
              </div>

              {/* Pending Tasks Checklist */}
              <div>
                <h4 style={{ fontSize: '0.825rem', fontWeight: 700, color: '#475569', textTransform: 'uppercase', marginBottom: '0.4rem' }}>
                  Pending Operational Clearance Tasks Delaying Release:
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                  {discharge.pending_tasks.map((task, idx) => (
                    <div
                      key={idx}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        fontSize: '0.85rem',
                        color: '#991b1b',
                        background: '#fef2f2',
                        border: '1px solid #fee2e2',
                        padding: '0.4rem 0.65rem',
                        borderRadius: '4px',
                        fontWeight: 500,
                      }}
                    >
                      <AlertOctagon size={14} color="#dc2626" />
                      <span>{task}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
